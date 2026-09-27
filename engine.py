"""
AnO Media Letter Generator — core engine.

Approach
--------
Every source template PDF (Employment Agreement, Offer Letter, Relieving
Letter, Experience Letter, Recommendation Letter) already IS the official
AnO Media letterhead — logos, colours, footer bars, page numbering, and the
Director's signature stamp are all real vector/image content baked into
those PDFs. So instead of rebuilding the design from scratch, this engine
opens the original template, surgically erases *only* the placeholder text
runs (the "<...>" tokens and the his/her/she/he pronoun slashes), and
redraws the correct value in the same font/size/position. Nothing else on
the page is touched, so the design can never drift from the original.

Two kinds of fields are handled:

  * LINE fields  -- a placeholder that sits alone on its own line with
    plenty of blank space after it (Ref No, Date, "Position: <>", a
    printed name under a signature line, etc). These are replaced with a
    single direct redact + insert at the same baseline.

  * PARAGRAPH fields -- a placeholder embedded inside flowing prose
    ("...appointed as <Position> with effect from <Date>, at the
    Company's..."). Because the real value may be a different length than
    the "<Position>" token, the whole paragraph is erased and re-wrapped
    from scratch at the same start point / column width / font / leading,
    so the text always flows cleanly no matter how long the filled-in
    value is.

Fonts: every template uses a Times-New-Roman-a-like face (embedded as
"TimesNRMTPro" or "TeXGyreTermes"). Rather than depend on those embedded,
subsetted font programs (which only contain the glyphs the original PDF
happened to use), we render replacement text with the PDF standard
Times-Roman / Times-Bold fonts, which are metrically near-identical and
guaranteed to be available in any PDF viewer with a full glyph set.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import pymupdf as fitz

FONT_REGULAR = "Times-Roman"
FONT_BOLD = "Times-Bold"

WHITE = (1, 1, 1)
BLACK = (0, 0, 0)
GRAY_PAGENO = (166 / 255, 166 / 255, 166 / 255)


# --------------------------------------------------------------------------
# Data model
# --------------------------------------------------------------------------

@dataclass
class LineField:
    """A placeholder that lives alone on one line (no re-wrap needed)."""
    page: int
    origin: tuple[float, float]      # baseline (x, y) of the ORIGINAL run being replaced
    template: str                    # e.g. "{ref_no}"  or  "Position: {position}"
    bold: bool = False
    fontsize: float = 12.0
    erase_rect: Optional[tuple[float, float, float, float]] = None
    color: tuple[float, float, float] = BLACK


@dataclass
class Run:
    """One styled fragment inside a paragraph template."""
    template: str
    bold: bool = False


@dataclass
class ParaField:
    """A placeholder embedded in flowing prose; erased and re-wrapped."""
    page: int
    erase_rect: Optional[tuple[float, float, float, float]]   # single erase region (or None if using erase_rects)
    origin: tuple[float, float]                      # baseline of the paragraph's FIRST line
    max_width: float
    runs: list[Run]
    fontsize: float = 12.0
    leading: float = 16.5
    color: tuple[float, float, float] = BLACK
    erase_rects: Optional[list[tuple[float, float, float, float]]] = None  # use instead of erase_rect when the
                                                                            # region isn't a single rectangle
                                                                            # (e.g. must dodge a glyph in a
                                                                            # different font, like the ₹ sign)
    left_margin: Optional[float] = None  # x where WRAPPED (2nd+) lines start; defaults to origin[0].
                                          # Set this when the first line starts indented (e.g. right after
                                          # a symbol on the same line) but continuation lines should return
                                          # to the paragraph's normal left margin.


@dataclass
class LetterTemplate:
    source_pdf: str
    letter_code: str                 # used in output filename, e.g. "Offer"
    line_fields: list[LineField] = field(default_factory=list)
    para_fields: list[ParaField] = field(default_factory=list)


# --------------------------------------------------------------------------
# Pronoun helper
# --------------------------------------------------------------------------

PRONOUNS = {
    "male":   {"He": "He", "he": "he", "His": "His", "his": "his", "Him": "Him", "him": "him",
               "She": "He", "she": "he", "Her": "His", "her": "his", "Hers": "His"},
    "female": {"He": "She", "he": "she", "His": "Her", "his": "her", "Him": "Her", "him": "her",
               "She": "She", "she": "she", "Her": "Her", "her": "her", "Hers": "Hers"},
}


def pronoun_kwargs(gender: str) -> dict:
    """Returns a dict of every pronoun token used across the templates,
    resolved for the given gender, ready to feed into str.format(**kwargs).
    gender must be 'male' or 'female'.
    """
    g = gender.lower()
    if g not in ("male", "female"):
        raise ValueError("gender must be 'male' or 'female'")
    he = "he" if g == "male" else "she"
    return {
        "He": he.capitalize(), "he": he,
        "His": ("his" if g == "male" else "her").capitalize(),
        "his": "his" if g == "male" else "her",
        "Him": ("him" if g == "male" else "her").capitalize(),
        "him": "him" if g == "male" else "her",
        "She": he.capitalize(), "she": he,      # in case a template writes She/He literally
        "Her": ("his" if g == "male" else "her").capitalize(),
        "her": "his" if g == "male" else "her",
    }


# --------------------------------------------------------------------------
# Work-location helper (Employment Agreement only)
# --------------------------------------------------------------------------

# The original template wrote both options in one slash-separated sentence
# ("...at the Company's office at Lam Road, Nashik,/at a remote location
# (work from home)..."). This resolves a single choice instead, exactly as
# for gender/pronouns: pass work_mode="office" or "remote" in `data` and
# {work_location} in a Run template resolves to the right phrase. Letter
# types that don't use "work_mode" are unaffected — see generate_letter().
WORK_LOCATION_TEXT = {
    "office": "at the Company's office at Lam Road, Nashik",
    "remote": "at a remote location (work from home)",
}


def work_location_kwargs(work_mode: str) -> dict:
    mode = work_mode.lower()
    if mode not in WORK_LOCATION_TEXT:
        raise ValueError("work_mode must be 'office' or 'remote'")
    return {"work_location": WORK_LOCATION_TEXT[mode]}


# --------------------------------------------------------------------------
# Low level drawing helpers
# --------------------------------------------------------------------------

def _text_len(text: str, bold: bool, fontsize: float) -> float:
    fontname = FONT_BOLD if bold else FONT_REGULAR
    return fitz.get_text_length(text, fontname=fontname, fontsize=fontsize)


def _tokenize(runs: list[Run]) -> list[tuple[str, bool]]:
    """Splits styled runs into (word_with_trailing_space, bold) tokens,
    keeping style boundaries intact so words never merge two styles."""
    tokens: list[tuple[str, bool]] = []
    for run in runs:
        text = run.template
        # keep spaces attached to the preceding word so wrapping math is simple
        parts = re.findall(r"\S+\s*|\s+", text)
        for part in parts:
            tokens.append((part, run.bold))
    return tokens


def draw_paragraph(page: "fitz.Page", pf: ParaField, data: dict) -> None:
    """Erases pf.erase_rect(s) and redraws pf.runs (after .format(**data))
    wrapped to pf.max_width. The first line starts at pf.origin; any
    wrapped continuation lines return to pf.left_margin (or origin[0] if
    left_margin is not set)."""
    # 1. erase the old paragraph text only. fill=None (no cover rectangle)
    # so any faint background artwork under the text is left completely
    # untouched instead of being painted over with a white box.
    rects = pf.erase_rects if pf.erase_rects else [pf.erase_rect]
    for r in rects:
        page.add_redact_annot(fitz.Rect(*r), fill=None)
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)

    # 2. resolve the templated text
    resolved_runs = [Run(r.template.format(**data), r.bold) for r in pf.runs]
    tokens = _tokenize(resolved_runs)

    x0, y0 = pf.origin
    wrap_x0 = pf.left_margin if pf.left_margin is not None else x0
    x, y = x0, y0
    right_edge = wrap_x0 + pf.max_width
    line_start_x = x0  # the left edge of the CURRENT line (differs on line 1 only)

    for word, bold in tokens:
        if word.isspace():
            # a space at the very start of a wrapped line is dropped
            if x == line_start_x:
                continue
            w = _text_len(word, bold, pf.fontsize)
            x += w
            continue
        w = _text_len(word, bold, pf.fontsize)
        if x + w > right_edge and x > line_start_x:
            # wrap to next line, returning to the paragraph's normal margin
            line_start_x = wrap_x0
            x = wrap_x0
            y += pf.leading
        page.insert_text((x, y), word, fontname=FONT_BOLD if bold else FONT_REGULAR,
                          fontsize=pf.fontsize, color=pf.color)
        x += w


def draw_line(page: "fitz.Page", lf: LineField, data: dict) -> None:
    text = lf.template.format(**data)
    if lf.erase_rect:
        page.add_redact_annot(fitz.Rect(*lf.erase_rect), fill=None)
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
    page.insert_text(lf.origin, text, fontname=FONT_BOLD if lf.bold else FONT_REGULAR,
                      fontsize=lf.fontsize, color=lf.color)


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------

def generate_letter(template: LetterTemplate, data: dict, gender: str,
                     recipient_name: str, templates_dir: Path, output_dir: Path) -> Path:
    """Fills `template` with `data` (+ pronouns resolved for `gender`) and
    writes  "<LetterCode> letter - <recipient_name>.pdf"  into output_dir.
    If `data` includes "work_mode" ("office" or "remote"), {work_location}
    is resolved too (used by the Employment Agreement's Section 1 clause).
    """
    merged = {**data, **pronoun_kwargs(gender)}
    if "work_mode" in data:
        merged.update(work_location_kwargs(data["work_mode"]))

    doc = fitz.open(str(templates_dir / template.source_pdf))
    try:
        for lf in template.line_fields:
            draw_line(doc[lf.page], lf, merged)
        for pf in template.para_fields:
            draw_paragraph(doc[pf.page], pf, merged)

        output_dir.mkdir(parents=True, exist_ok=True)
        safe_name = re.sub(r'[\\/*?:"<>|]', "", recipient_name).strip()
        out_path = output_dir / f"{template.letter_code} letter - {safe_name}.pdf"
        doc.save(str(out_path))
        return out_path
    finally:
        doc.close()

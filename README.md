# AnO Media Letter Generator

Fills in your 5 HR templates (Employment Agreement, Offer/Appointment
Letter, Relieving Letter, Experience Letter, Recommendation Letter) and
outputs a ready-to-send PDF, named `"<Type> letter - <Name>.pdf"`.

**Want HR to use this without touching Python?** There's now a small web
app (`streamlit_app.py`) — pick a letter type, fill in a form, download the
PDF. Run it locally with `streamlit run streamlit_app.py`, or see
**DEPLOY.md** for how to put it on a real URL the whole HR team can use.

## How it actually works

Your template PDFs aren't images — they're real PDFs with real text, built
on your official letterhead (logo, colours, footer bar, page numbers, and
Kanishka's signature stamp are all already baked in). So this tool doesn't
rebuild anything: it opens your original template, **surgically erases only
the placeholder text** (`<name>`, `<position>`, the his/her slashes, etc.)
and redraws the correct value in the same font, size and position. Every
pixel of the design you didn't ask to change stays byte-for-byte the same.

Two kinds of fields are handled differently:

- **Line fields** — a placeholder alone on its own line with room to spare
  (Ref No, Date, "Position: `<>`"). Replaced directly, no reflow needed.
- **Paragraph fields** — a placeholder inside a flowing sentence (`"...as a
  <position> with effect from <date>..."`). The whole paragraph is erased
  and **re-wrapped from scratch**, so if your real value is longer or
  shorter than the placeholder, the sentence still wraps cleanly instead of
  overlapping the next line.

His/her/him is resolved the same way everywhere: pass `gender="male"` or
`gender="female"` and every pronoun in the letter — including a couple of
places where your original templates use a bare "her"/"his" instead of the
"her/his" slash form — resolves automatically.

## Files

```
engine.py         Core reusable engine (wrapping, redaction, drawing, pronouns)
templates.py      Per-letter-type field maps (exact coordinates + wording)
generate.py       Example usage / thin CLI
hr_helpers.py     Non-UI logic for the web app (serial numbers, audit log)
streamlit_app.py  The web form HR actually uses (see DEPLOY.md to host it)
test_hr_helpers.py  pytest tests for hr_helpers.py — `pytest test_hr_helpers.py`
DEPLOY.md         How to put streamlit_app.py on a URL the HR team can reach
templates_src/    Your original 5 template PDFs + letterhead.pdf + signature PNG
output/           Generated letters land here
data/             Serial-number counter + audit log (created on first run)
```

## Running it

```bash
pip install pymupdf
python generate.py        # generates one sample of every letter type into output/
```

To generate a real letter from your own code (a form, a script, a small
Streamlit/Flask app — whatever you build on top):

```python
from generate import generate_one

generate_one(
    "relieving", "female", "Priya Sharma",       # letter_type, gender, name-for-filename
    name="Priya Sharma", position="Content Strategist",
    start_date="1 January 2025", end_date="30 June 2026",
    mmyy="0926", serial="014", date="15 September 2026",
)
```

`letter_type` is one of: `relieving`, `experience`, `recommendation`,
`offer`, `employment`. The required field names for each type are listed at
the bottom of `templates.py` (`RELIEVING_FIELDS`, `OFFER_FIELDS`, etc.) —
call `generate_one` without one and it'll tell you exactly what's missing.

## Adding a 6th letter type (e.g. Influencer Agreement) — two options

**A. You have a template PDF for it (recommended, matches this tool's approach).**
Drop the PDF into `templates_src/`, then run this once to see every
placeholder's exact position:

```python
import fitz
d = fitz.open("templates_src/Your_New_Template.pdf")
for pno, p in enumerate(d):
    for b in p.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                print(pno, s["origin"], s["bbox"], s["text"])
```
Use those origins/bboxes to add a new `LetterTemplate(...)` block in
`templates.py`, following the pattern of the 5 already there.

**B. You don't have a template yet — build one from the blank letterhead.**
`templates_src/letterhead.pdf` has page 0 (first-page background: logo +
header) and page 1 (continuation-page background: just the corner
graphics, for page 2 onward) with nothing else on them.
`templates_src/signature_transparent.png` is Kanishka's signature with the
background removed, for stamping onto a blank page (the 5 existing
templates already have this stamp baked in as a JPEG, so you don't need
this file for them). Build the new letter's body text with ReportLab's
`Platypus` flowables on top of those two backgrounds (one `PageTemplate`
per background) — happy to build this out fully once you've got a first
draft of the wording.

## Known limitations (v1)

- **Vertical rhythm on reflow:** each paragraph keeps its original starting
  Y position. If your real text produces noticeably more or fewer lines
  than the placeholder text did, the gap before the *next* paragraph can
  look very slightly uneven (a line or so). It's barely visible in the
  samples in `output/`, but for pixel-perfect spacing regardless of content
  length, the fix is a fully dynamic flowing layout (one continuous story
  instead of fixed-position paragraphs) — happy to build that next if it
  matters for your use case.
- **Very long values** in tight single-line fields (e.g. an unusually long
  job title in the Offer Letter's "Position: ..." line) could in principle
  run close to the page edge — normal names/titles/dates are nowhere close
  to this limit in testing.
- Two small wording quirks in your original templates were corrected as
  part of "resolve every his/her disparity": the Experience Letter's
  "...carried out **her** responsibilities..." and "...appreciated by both
  **her** colleagues..." now correctly resolve to the stated gender instead
  of always saying "her". Same for the Recommendation Letter's "...both
  **her** peers...". Flag it if you'd rather I leave those exactly as
  originally written.

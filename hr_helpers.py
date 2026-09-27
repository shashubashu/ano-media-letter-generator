"""
Non-UI helpers for the HR letter generator: field labels/defaults, the
Ref. No. serial counter, and the generation audit log. Kept dependency-free
(no `streamlit` import) so this can be unit-tested with plain pytest/python
and reused by any future front end (Streamlit, a CLI, a Slack bot, etc).
"""

import csv
import json
from datetime import date, datetime
from pathlib import Path

LETTER_TYPES = {
    "Relieving Letter": "relieving",
    "Experience Letter": "experience",
    "Recommendation Letter": "recommendation",
    "Offer / Appointment Letter": "offer",
    "Employment Agreement": "employment",
}

REF_PREFIX = {
    "relieving": "AnO/HR",
    "experience": "AnO/HR",
    "recommendation": "AnO/HR",
    "offer": "AnO/HR",
    "employment": "AnO/HR",
}
REF_SUFFIX = {"relieving": "RvL", "experience": "ExpL", "recommendation": "RecL"}


def _today_long() -> str:
    return date.today().strftime("%-d %B %Y")


def _mmyy() -> str:
    return date.today().strftime("%m%y")


# Per-field: (label, help text, default). "default" is a plain string or a
# zero-arg callable evaluated fresh each time it's needed (e.g. today's date).
FIELD_META = {
    "name":               ("Employee / candidate full name", "Exactly as it should appear on the letter.", ""),
    "position":           ("Position / role title", "", ""),
    "role":               ("Role", "", ""),
    "address":            ("Address", "Full postal address.", ""),
    "start_date":         ("Start date", "", _today_long),
    "end_date":           ("End date (last working day)", "", _today_long),
    "start_to_end_date":  ("Employment period", 'e.g. "4 July 2023 to 31 August 2026"', ""),
    "joining_date":       ("Joining date", "", _today_long),
    "return_by_date":     ("Offer must be signed & returned by", "", _today_long),
    "location":           ("Work location", "", "Nashik"),
    "compensation":       ("Compensation (as shown on the letter)", 'e.g. "Rs. 35,000"', ""),
    "salary_figure":      ("Monthly salary — figures", 'e.g. "45,000" (goes after the ₹ symbol)', ""),
    "salary_words":       ("Monthly salary — in words (thousands)", 'e.g. "45" for "Forty-Five Thousand"', ""),
    "date":               ("Letter date", "", _today_long),
    "mmyy":               ("Ref. No. month/year code", 'e.g. "0926" for Sept 2026', _mmyy),
    "serial":             ("Ref. No. serial", "Auto-suggested from the last one used; edit if needed.", ""),
}


def label_for(field: str) -> str:
    meta = FIELD_META.get(field)
    return meta[0] if meta else field.replace("_", " ").capitalize()


def help_for(field: str) -> str:
    meta = FIELD_META.get(field)
    return meta[1] if meta else ""


def default_for(field: str) -> str:
    meta = FIELD_META.get(field)
    if not meta:
        return ""
    d = meta[2]
    return d() if callable(d) else d


def ref_no_preview(letter_type: str, values: dict) -> str:
    suffix = REF_SUFFIX.get(letter_type)
    prefix = REF_PREFIX[letter_type] + (f"-{suffix}" if suffix else "")
    if letter_type == "relieving":
        return f"{prefix}/{values.get('mmyy', '')}/{values.get('serial', '')}"
    return f"{prefix}/{values.get('serial', '')}"


class SerialCounter:
    """Tracks the last-used Ref. No. serial per letter type in a small JSON
    file. Good enough for a single small server; if you outgrow a single
    always-on host (multiple concurrent instances, need a shared source of
    truth), move this to a database or a Google Sheet instead — see
    DEPLOY.md."""

    def __init__(self, path: Path):
        self.path = path

    def _read(self) -> dict:
        return json.loads(self.path.read_text()) if self.path.exists() else {}

    def next(self, letter_type: str) -> str:
        return f"{self._read().get(letter_type, 0) + 1:03d}"

    def record_used(self, letter_type: str, used_value: str) -> None:
        """Best-effort: only advances the counter if the serial used was a
        plain integer, so a manual/non-numeric override can't corrupt it."""
        if not str(used_value).isdigit():
            return
        counters = self._read()
        counters[letter_type] = max(counters.get(letter_type, 0), int(used_value))
        self.path.write_text(json.dumps(counters))


class GenerationLog:
    """Append-only CSV audit trail of every letter generated: who, what,
    when, for whom. Deliberately excludes compensation/salary/address so
    the log itself stays low-sensitivity even though the PDFs it points to
    are not."""

    FIELDNAMES = ["timestamp", "generated_by", "letter_type", "ref_no", "recipient_name"]

    def __init__(self, path: Path):
        self.path = path

    def append(self, generated_by: str, letter_type: str, ref_no: str, recipient_name: str) -> None:
        is_new = not self.path.exists()
        with open(self.path, "a", newline="") as f:
            w = csv.writer(f)
            if is_new:
                w.writerow(self.FIELDNAMES)
            w.writerow([datetime.now().isoformat(timespec="seconds"), generated_by, letter_type,
                        ref_no, recipient_name])

    def tail(self, n: int = 10) -> list[list[str]]:
        if not self.path.exists():
            return []
        with open(self.path) as f:
            rows = list(csv.reader(f))[1:]
        return rows[-n:]

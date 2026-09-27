"""
Example usage / thin CLI for the AnO Media letter generator.

    python generate.py relieving female \
        name="Priya Sharma" position="Content Strategist" \
        start_date="1 Jan 2025" end_date="30 Jun 2026" \
        mmyy="0926" serial="014" date="15 Sep 2026"

Or import and call generate_one(...) directly from your own code /
a small Flask/FastAPI form, a Streamlit app, etc. -- see the bottom of
this file for a fully worked Python example for every letter type.
"""

from pathlib import Path

from engine import generate_letter
from templates import ALL_TEMPLATES

TEMPLATES_DIR = Path(__file__).parent / "templates_src"
OUTPUT_DIR = Path(__file__).parent / "output"


def generate_one(letter_type: str, gender: str, recipient_name: str, **fields) -> Path:
    """letter_type: one of 'relieving','experience','recommendation','offer','employment'
    gender: 'male' or 'female'
    recipient_name: used only to build the output filename
    **fields: every key listed in that template's *_FIELDS list, e.g. name=,
              position=, start_date=, end_date=, serial=, date=, ...
    """
    if letter_type not in ALL_TEMPLATES:
        raise ValueError(f"Unknown letter_type '{letter_type}'. Choose from {list(ALL_TEMPLATES)}")
    template, required = ALL_TEMPLATES[letter_type]
    missing = [f for f in required if f not in fields]
    if missing:
        raise ValueError(f"Missing required fields for '{letter_type}': {missing}")
    return generate_letter(template, fields, gender, recipient_name, TEMPLATES_DIR, OUTPUT_DIR)


if __name__ == "__main__":
    # ---- one worked example per letter type -----------------------------
    generate_one(
        "relieving", "female", "Priya Sharma",
        name="Priya Sharma", position="Content Strategist",
        start_date="1 January 2025", end_date="30 June 2026",
        mmyy="0926", serial="014", date="15 September 2026",
    )

    generate_one(
        "experience", "male", "Rohan Verma",
        name="Rohan Verma", position="Video Editor",
        start_date="12 March 2024", end_date="10 September 2026",
        serial="015", date="15 September 2026",
    )

    generate_one(
        "recommendation", "female", "Ananya Iyer",
        name="Ananya Iyer", role="Social Media Manager",
        start_to_end_date="4 July 2023 to 31 August 2026",
        serial="016", date="15 September 2026",
    )

    generate_one(
        "offer", "male", "Arjun Mehta",
        name="Arjun Mehta", address="14, Lake View Society, Gangapur Road, Nashik - 422013",
        position="Performance Marketing Executive", start_date="1 October 2026",
        location="Nashik (on-site)", compensation="Rs. 35,000",
        joining_date="1 October 2026", return_by_date="22 September 2026",
        serial="017", date="15 September 2026",
    )

    generate_one(
        "employment", "female", "Sneha Kulkarni",
        name="Sneha Kulkarni", address="221, Model Colony, Nashik - 422002",
        position="Senior Content Writer", start_date="1 October 2026",
        work_mode="office",  # or "remote" for work-from-home
        salary_figure="45,000", salary_words="45",
        serial="018", date="15 September 2026",
    )

    print("Generated sample letters into:", OUTPUT_DIR.resolve())

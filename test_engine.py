"""
Run with:  pytest test_engine.py
Covers the small pure-logic helpers in engine.py (pronoun and work-location
resolution). PDF generation itself is exercised in generate.py's worked
examples and by visual inspection during development.
"""

import pytest

from engine import pronoun_kwargs, work_location_kwargs


def test_pronoun_kwargs_male():
    p = pronoun_kwargs("male")
    assert p["He"] == "He" and p["he"] == "he"
    assert p["His"] == "His" and p["his"] == "his"
    assert p["him"] == "him"


def test_pronoun_kwargs_female():
    p = pronoun_kwargs("female")
    assert p["He"] == "She" and p["he"] == "she"
    assert p["His"] == "Her" and p["his"] == "her"
    assert p["him"] == "her"


def test_pronoun_kwargs_rejects_bad_input():
    with pytest.raises(ValueError):
        pronoun_kwargs("other")


def test_pronoun_kwargs_case_insensitive():
    assert pronoun_kwargs("Male") == pronoun_kwargs("male")


def test_work_location_office():
    assert work_location_kwargs("office")["work_location"] == \
        "at the Company's office at Lam Road, Nashik"


def test_work_location_remote():
    assert work_location_kwargs("remote")["work_location"] == \
        "at a remote location (work from home)"


def test_work_location_rejects_bad_input():
    with pytest.raises(ValueError):
        work_location_kwargs("hybrid")

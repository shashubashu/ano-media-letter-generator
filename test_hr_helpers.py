"""
Run with:  pytest test_hr_helpers.py
Covers the non-UI logic only (hr_helpers.py). The PDF-generation engine
itself is exercised in generate.py's worked examples.
"""

import tempfile
from pathlib import Path

import pytest

from hr_helpers import SerialCounter, GenerationLog, ref_no_preview


def test_serial_counter_increments():
    with tempfile.TemporaryDirectory() as d:
        c = SerialCounter(Path(d) / "counter.json")
        assert c.next("relieving") == "001"
        c.record_used("relieving", "001")
        assert c.next("relieving") == "002"
        # a different letter type has its own independent count
        assert c.next("offer") == "001"


def test_serial_counter_ignores_non_numeric_override():
    with tempfile.TemporaryDirectory() as d:
        c = SerialCounter(Path(d) / "counter.json")
        c.record_used("relieving", "SPECIAL-001")  # HR typed something custom
        assert c.next("relieving") == "001"  # counter wasn't corrupted


def test_serial_counter_does_not_go_backwards():
    with tempfile.TemporaryDirectory() as d:
        c = SerialCounter(Path(d) / "counter.json")
        c.record_used("relieving", "010")
        c.record_used("relieving", "003")  # someone typed an old number by hand
        assert c.next("relieving") == "011"  # still advances from the highest seen


def test_generation_log_roundtrip():
    with tempfile.TemporaryDirectory() as d:
        log = GenerationLog(Path(d) / "log.csv")
        log.append("Asha", "relieving", "001", "Priya Sharma")
        log.append("Asha", "offer", "001", "Arjun Mehta")
        rows = log.tail()
        assert len(rows) == 2
        assert rows[0][4] == "Priya Sharma"
        assert rows[1][4] == "Arjun Mehta"


def test_ref_no_preview_relieving_includes_mmyy():
    preview = ref_no_preview("relieving", {"mmyy": "0926", "serial": "014"})
    assert preview == "AnO/HR-RvL/0926/014"


def test_ref_no_preview_offer_has_no_suffix():
    preview = ref_no_preview("offer", {"serial": "017"})
    assert preview == "AnO/HR/017"

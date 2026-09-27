"""
AnO Media HR Letter Generator — internal web app.

Run locally:      streamlit run streamlit_app.py
Deploy:            see DEPLOY.md in this folder.

This file is UI only. All PDF logic lives in engine.py / templates.py, and
all non-UI helper logic (serials, audit log, field labels) lives in
hr_helpers.py so it can be tested without a browser.
"""

from pathlib import Path

import streamlit as st

from engine import generate_letter
from templates import ALL_TEMPLATES
from hr_helpers import (
    LETTER_TYPES, GenerationLog, SerialCounter,
    default_for, help_for, label_for, ref_no_preview,
)

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates_src"
OUTPUT_DIR = BASE_DIR / "output"
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

serials = SerialCounter(DATA_DIR / "serial_counter.json")
log = GenerationLog(DATA_DIR / "generation_log.csv")

st.set_page_config(page_title="AnO Media — HR Letter Generator", page_icon="📄", layout="centered")

# ---------------------------------------------------------------------------
# Access gate — swap this for real SSO/login before wider rollout (see
# DEPLOY.md). This is only a light deterrent against a stray public link,
# not real access control: the shared password lives in plain text in
# secrets.toml, anyone with it can use the tool, and there's no per-person
# identity beyond the free-text "Your name" field below.
# ---------------------------------------------------------------------------
REQUIRED_PASSWORD = st.secrets.get("HR_PASSWORD", None)
if REQUIRED_PASSWORD:
    if "authed" not in st.session_state:
        st.session_state.authed = False
    if not st.session_state.authed:
        st.title("AnO Media — HR Letter Generator")
        pwd = st.text_input("Team password", type="password")
        if st.button("Enter"):
            if pwd == REQUIRED_PASSWORD:
                st.session_state.authed = True
                st.rerun()
            else:
                st.error("Incorrect password.")
        st.stop()

# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
st.title("📄 AnO Media — HR Letter Generator")
st.caption("Generates a ready-to-send PDF on the official letterhead. Nothing is emailed automatically — "
           "review the download before sending it out.")

with st.sidebar:
    st.subheader("Session")
    generated_by = st.text_input("Your name", help="Recorded in the internal generation log only.")
    st.divider()
    st.caption("Last few letters generated (this server):")
    for r in reversed(log.tail(10)):
        st.caption(f"{r[0][:16]} — {r[2]} — {r[4]}")

letter_label = st.selectbox("Letter type", list(LETTER_TYPES.keys()))
letter_type = LETTER_TYPES[letter_label]
template, required_fields = ALL_TEMPLATES[letter_type]

gender = st.radio("Employee's gender (resolves his/her/him wording)", ["Female", "Male"], horizontal=True)

st.markdown("---")
st.subheader("Letter details")

values = {}
col1, col2 = st.columns(2)
text_fields = [f for f in required_fields if f not in ("serial", "work_mode")]
for i, f in enumerate(text_fields):
    target_col = col1 if i % 2 == 0 else col2
    values[f] = target_col.text_input(label_for(f), value=default_for(f), help=help_for(f),
                                       key=f"in_{letter_type}_{f}")

if "work_mode" in required_fields:
    WORK_MODE_LABELS = {"Office (Lam Road, Nashik)": "office", "Remote (Work From Home)": "remote"}
    choice = st.radio("Employee's work location", list(WORK_MODE_LABELS.keys()),
                       horizontal=True, key=f"in_{letter_type}_work_mode")
    values["work_mode"] = WORK_MODE_LABELS[choice]

if "serial" in required_fields:
    values["serial"] = col1.text_input(label_for("serial"), value=serials.next(letter_type),
                                        help=help_for("serial"), key=f"in_{letter_type}_serial")
    st.caption(f"Ref. No. preview: {ref_no_preview(letter_type, values)}")

st.markdown("---")

missing = [f for f in required_fields if not values.get(f, "").strip()]
generate_clicked = st.button("Generate letter", type="primary", disabled=bool(missing))
if missing:
    st.caption("Fill in every field above to enable generation: " + ", ".join(label_for(m) for m in missing))

if generate_clicked:
    try:
        path = generate_letter(template, values, gender.lower(), values["name"], TEMPLATES_DIR, OUTPUT_DIR)
        serials.record_used(letter_type, values.get("serial", ""))
        log.append(generated_by or "(not given)", letter_label, values.get("serial", ""), values["name"])
        st.success(f"Generated: {path.name}")
        with open(path, "rb") as f:
            st.download_button("⬇ Download PDF", f.read(), file_name=path.name, mime="application/pdf")
    except Exception as e:
        st.error(f"Could not generate the letter: {e}")

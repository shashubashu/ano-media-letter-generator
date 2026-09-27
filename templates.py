"""
Field configuration for every letter type.

For each letter, `data` must supply the keys referenced in that letter's
"required_fields" list. Gender ("male"/"female") is passed separately and
resolves every his/her/him/she/he occurrence automatically.

Coordinates below were extracted directly from the supplied template PDFs
(pdf points, top-left origin) using PyMuPDF, so replacement text lands
exactly where the original placeholder text sat.
"""

from engine import LetterTemplate, LineField, ParaField, Run

# ---------------------------------------------------------------------------
# 1. RELIEVING LETTER
# ---------------------------------------------------------------------------
RELIEVING = LetterTemplate(
    source_pdf="Relieving_Letter_-_template.pdf",
    letter_code="Relieving",
    line_fields=[
        LineField(page=0, origin=(95.6, 171.91), template=": AnO/HR-RvL/{mmyy}/{serial}",
                  erase_rect=(95.6, 161.8, 440, 177.3)),
        LineField(page=0, origin=(475.58, 171.91), template=" {date}",
                  erase_rect=(475.58, 161.8, 540, 177.3)),
    ],
    para_fields=[
        ParaField(page=0, origin=(55.8, 259.71), max_width=484.2,
                  erase_rect=(54.8, 249.6, 540.0, 281.6),
                  runs=[
                      Run("This is to certify that ", False),
                      Run("{name}", True),
                      Run(" was employed with AnO Media Pvt. Ltd. as a ", False),
                      Run("{position}", True),
                      Run(" from ", False),
                      Run("{start_date}", True),
                      Run(" to ", False),
                      Run("{end_date}", True),
                      Run(".", False),
                  ]),
        ParaField(page=0, origin=(55.8, 309.23), max_width=484.2,
                  erase_rect=(54.8, 299.1, 540.0, 364.1),
                  runs=[
                      Run("{His} resignation has been accepted by the Company, and {he} has been relieved "
                          "from {his} duties with effect from ", False),
                      Run("{end_date}", True),
                      Run(". {He} has completed all handover formalities and has no outstanding "
                          "obligations or dues pending with the Company as of {his} last working day.", False),
                  ]),
        ParaField(page=0, origin=(55.8, 391.76), max_width=484.2,
                  erase_rect=(54.8, 381.6, 540.0, 413.7),
                  runs=[
                      Run("We thank {him} for {his} services and wish {him} every success in {his} "
                          "future professional pursuits.", False),
                  ]),
    ],
)
RELIEVING_FIELDS = ["mmyy", "serial", "date", "name", "position", "start_date", "end_date"]

# ---------------------------------------------------------------------------
# 2. EXPERIENCE LETTER
# ---------------------------------------------------------------------------
EXPERIENCE = LetterTemplate(
    source_pdf="Experience_Letter_-_Template.pdf",
    letter_code="Experience",
    line_fields=[
        LineField(page=0, origin=(95.6, 171.91), template=": AnO/HR-ExpL/{serial}",
                  erase_rect=(95.6, 161.8, 440, 177.3)),
        LineField(page=0, origin=(475.58, 171.91), template=" {date}",
                  erase_rect=(475.58, 161.8, 540, 177.3)),
    ],
    para_fields=[
        ParaField(page=0, origin=(55.8, 231.84), max_width=484.2,
                  erase_rect=(54.8, 221.7, 540.0, 253.8),
                  runs=[
                      Run("This is to certify that ", False),
                      Run("{name}", True),
                      Run(" was employed with ", False),
                      Run("AnO Media Pvt. Ltd.", True),
                      Run(" as a ", False),
                      Run("{position}", True),
                      Run(" from ", False),
                      Run("{start_date}", True),
                      Run(", to ", False),
                      Run("{end_date}", True),
                      Run(".", False),
                  ]),
        # NOTE: the original template text reads "...carried out her
        # responsibilities..." and "...appreciated by both her/his..."
        # inconsistently (sometimes missing the "/his" toggle). Per your
        # instruction to resolve every his/her disparity, every occurrence
        # below is treated as gender-resolved, not just the slashed ones.
        ParaField(page=0, origin=(55.8, 281.36), max_width=484.2,
                  erase_rect=(54.8, 271.3, 540.0, 319.8),
                  runs=[
                      Run("During {his} tenure with the organization, {he} carried out {his} "
                          "responsibilities diligently and contributed positively to the team's "
                          "objectives. {His} professionalism, commitment, and work ethic were "
                          "appreciated by both {his} colleagues and management.", False),
                  ]),
        ParaField(page=0, origin=(55.8, 330.88), max_width=484.2,
                  erase_rect=(54.8, 320.8, 540.0, 352.8),
                  runs=[
                      Run("We thank {him} for {his} valuable contributions and wish {him} continued "
                          "success in all {his} future professional endeavors.", False),
                  ]),
    ],
)
EXPERIENCE_FIELDS = ["serial", "date", "name", "position", "start_date", "end_date"]

# ---------------------------------------------------------------------------
# 3. RECOMMENDATION LETTER
# ---------------------------------------------------------------------------
RECOMMENDATION = LetterTemplate(
    source_pdf="Recomendation_Letter_-_Template.pdf",
    letter_code="Recommendation",
    line_fields=[
        LineField(page=0, origin=(95.6, 171.91), template=": AnO/HR-RecL/{serial}",
                  erase_rect=(95.6, 161.8, 440, 177.3)),
        LineField(page=0, origin=(475.58, 171.91), template=" {date}",
                  erase_rect=(475.58, 161.8, 540, 177.3)),
    ],
    para_fields=[
        ParaField(page=0, origin=(55.8, 231.84), max_width=489.2,
                  erase_rect=(54.8, 221.7, 545, 253.8),
                  runs=[
                      Run("I am pleased to write this letter of recommendation for ", False),
                      Run("{name}", True),
                      Run(", who was employed with AnO Media Pvt. Ltd. as a ", False),
                      Run("{role}", True),
                      Run(" from ", False),
                      Run("{start_to_end_date}", True),
                      Run(".", False),
                  ]),
        ParaField(page=0, origin=(55.8, 281.36), max_width=489.2,
                  erase_rect=(54.8, 271.3, 545, 336.3),
                  runs=[
                      Run("During {his} tenure with our organization, {name} consistently demonstrated "
                          "a high level of professionalism, dedication, and responsibility in carrying "
                          "out {his} duties. {He} was involved in content creation, client communication, "
                          "and relationship management, and performed these responsibilities with "
                          "sincerity and efficiency.", False),
                  ]),
        ParaField(page=0, origin=(55.8, 363.89), max_width=489.2,
                  erase_rect=(54.8, 353.8, 545, 451.8),
                  runs=[
                      Run("{name} possesses strong written communication skills, a keen understanding "
                          "of client requirements, and an ability to manage multiple tasks effectively "
                          "while maintaining attention to detail. {She} worked collaboratively with "
                          "colleagues, adapted well to evolving project needs, and contributed positively "
                          "to the overall objectives of the team. {Her} commitment to delivering quality "
                          "work and maintaining professional relationships was appreciated by both {his} "
                          "peers and management.", False),
                  ]),
        ParaField(page=0, origin=(55.8, 479.44), max_width=489.2,
                  erase_rect=(54.8, 469.3, 545, 534.4),
                  runs=[
                      Run("Based on {his} performance and conduct during {his} association with us, "
                          "I am confident that {name} will be a valuable asset to any organization {he} "
                          "chooses to join. I wholeheartedly recommend {him} for opportunities that align "
                          "with {his} skills and experience.", False),
                  ]),
        ParaField(page=0, origin=(55.8, 545.46), max_width=489.2,
                  erase_rect=(54.8, 535.4, 545, 567.4),
                  runs=[
                      Run("We thank {name} for {his} valuable contributions to AnO Media Pvt. Ltd. and "
                          "wish {him} continued success in all {his} future professional endeavors.", False),
                  ]),
    ],
)
RECOMMENDATION_FIELDS = ["serial", "date", "name", "role", "start_to_end_date"]

# ---------------------------------------------------------------------------
# 4. OFFER / APPOINTMENT LETTER  (2 pages)
# ---------------------------------------------------------------------------
OFFER = LetterTemplate(
    source_pdf="Offer_Letter_-_Template.pdf",
    letter_code="Offer",
    line_fields=[
        LineField(page=0, origin=(91.96, 163.24), template=": AnO/HR/{serial}",
                  erase_rect=(91.96, 153.1, 443, 168.6)),
        LineField(page=0, origin=(444.07, 163.24), template="Date: {date}", bold=True,
                  erase_rect=(443.1, 153.1, 545, 168.6)),
        LineField(page=0, origin=(55.8, 278.92), template="{joining_date}", bold=True,
                  erase_rect=(54.8, 268.8, 300, 284.3)),
        LineField(page=0, origin=(55.8, 311.93), template="{name},",
                  erase_rect=(54.8, 301.8, 300, 317.3)),
        LineField(page=0, origin=(55.8, 328.44), template="{address}",
                  erase_rect=(54.8, 318.3, 400, 333.8)),
        LineField(page=0, origin=(55.8, 361.45), template="Dear {name},",
                  erase_rect=(54.8, 351.3, 300, 366.9)),
        LineField(page=0, origin=(55.8, 476.99), template="Position: {position}",
                  erase_rect=(54.8, 466.9, 300, 482.4)),
        LineField(page=0, origin=(55.8, 493.5), template="Start Date: {start_date}",
                  erase_rect=(54.8, 483.4, 300, 498.9)),
        LineField(page=0, origin=(55.8, 510.01), template="Location: {location}.",
                  erase_rect=(54.8, 499.9, 300, 515.4)),
        LineField(page=0, origin=(55.8, 526.51), template="Compensation: {compensation} Per month.",
                  erase_rect=(54.8, 516.4, 400, 531.9)),
        LineField(page=1, origin=(62.91, 292.93), template="{name}",
                  erase_rect=(61.9, 282.8, 300, 298.3)),
    ],
    para_fields=[
        ParaField(page=0, origin=(55.8, 394.46), max_width=489.2,
                  erase_rect=(54.8, 384.4, 545, 432.9),
                  runs=[
                      Run("We are pleased to extend an offer of employment to you for the position of ", False),
                      Run("{position}", True),
                      Run(" at ", False),
                      Run("AnO Media Pvt.Ltd", True),
                      Run(". After careful consideration, we believe your skills and experience align "
                          "well with our goals, and we are excited about the opportunity to have you "
                          "join our team.", False),
                  ]),
        ParaField(page=0, origin=(55.8, 543.02), max_width=489.2,
                  erase_rect=(54.8, 532.9, 545, 548.4),
                  runs=[
                      Run("To accept this offer, please sign and return the enclosed copy of this letter "
                          "by ", False),
                      Run("{return_by_date}", True),
                      Run(".", False),
                  ]),
        ParaField(page=1, origin=(62.91, 177.38), max_width=482.1,
                  erase_rect=(61.9, 167.3, 545, 199.3),
                  runs=[
                      Run("I, ", False),
                      Run("{name}", True),
                      Run(", accept the terms of employment as outlined in this offer letter and confirm "
                          "my intention to begin employment with ", False),
                      Run("AnO Media Pvt. Ltd", True),
                      Run(" on {joining_date}.", False),
                  ]),
    ],
)
OFFER_FIELDS = ["serial", "date", "joining_date", "name", "address", "position",
                "start_date", "location", "compensation", "return_by_date"]

# ---------------------------------------------------------------------------
# 5. EMPLOYMENT AGREEMENT  (7 pages; placeholders on pages 1, 2 and 7)
# ---------------------------------------------------------------------------
EMPLOYMENT = LetterTemplate(
    source_pdf="Employment_Agreement_final-_template_pdf__1_.pdf",
    letter_code="Employment Agreement",
    line_fields=[
        LineField(page=0, origin=(95.67, 172.85), template=": AnO/HR/{serial}",
                  erase_rect=(95.67, 162.8, 400, 178.2)),
        LineField(page=0, origin=(433.6, 172.85), template="{date}",
                  erase_rect=(433.6, 162.8, 545, 178.2)),
        LineField(page=6, origin=(59.55, 453.55), template="{name}", bold=True,
                  erase_rect=(58.5, 438.6, 300, 459.6)),
    ],
    para_fields=[
        # NOTE: original text uses curly quotes ("Employee.") which the
        # PDF standard Times-Roman font cannot render reliably; straight
        # quotes are used instead so the character always displays.
        ParaField(page=0, origin=(50.7, 385.4), max_width=494.3,
                  erase_rect=(49.7, 370.5, 545, 391.5),
                  runs=[
                      Run("{name}", True),
                      Run(", resident at ", False),
                      Run("{address}", True),
                      Run(", hereinafter referred to as the \"Employee.\"", False),
                  ]),
        ParaField(page=0, origin=(51.8, 575.95), max_width=488.2,
                  erase_rect=(50.8, 565.8, 540, 614.4),
                  runs=[
                      Run("The Employee is appointed as ", False),
                      Run("{position}", True),
                      Run(" with effect from ", False),
                      Run("{start_date}", True),
                      # {work_location} resolves to one of the two original
                      # slash-separated options based on work_mode="office"
                      # or "remote" (see engine.work_location_kwargs) —
                      # instead of printing both options with a slash.
                      Run(", {work_location} or such other location as reasonably required by "
                          "the Company.", False),
                  ]),
        # The "₹" glyph uses a different embedded font (NotoSans) than the
        # rest of the document because base Times has no rupee-sign glyph,
        # so it must never fall inside an erase rectangle. Two separate
        # erase regions are used: one for the tail of line 1 (starting
        # just after the ₹) and a full-width one for line 2, which also
        # clears the original (now-redundant) "statutory deductions."
        # line so our own re-wrapped copy of that phrase isn't duplicated.
        # left_margin sends any 2nd+ wrapped line back to the paragraph's
        # true left margin (46.8) instead of continuing under the ₹.
        ParaField(page=1, origin=(190.34, 129.93), max_width=493.2,
                  left_margin=46.8,
                  erase_rect=None,
                  erase_rects=[
                      (190.3, 116.0, 540, 134.0),
                      (45.8, 134.0, 540, 152.0),
                  ],
                  runs=[
                      Run("{salary_figure}/- (Rupees {salary_words} Thousand Only) per month, subject "
                          "to applicable statutory deductions.", False),
                  ]),
    ],
)
EMPLOYMENT_FIELDS = ["serial", "date", "name", "address", "position", "start_date",
                     "work_mode", "salary_figure", "salary_words"]

ALL_TEMPLATES = {
    "relieving": (RELIEVING, RELIEVING_FIELDS),
    "experience": (EXPERIENCE, EXPERIENCE_FIELDS),
    "recommendation": (RECOMMENDATION, RECOMMENDATION_FIELDS),
    "offer": (OFFER, OFFER_FIELDS),
    "employment": (EMPLOYMENT, EMPLOYMENT_FIELDS),
}

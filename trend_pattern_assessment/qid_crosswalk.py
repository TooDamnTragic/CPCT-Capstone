"""
qid_crosswalk.py
================
QID-to-column-name crosswalk for the CPTC survey dataset.

BACKGROUND
----------
Every Qualtrics export stores three header rows before data begins:
  Row 0  – Column variable name  (e.g. "Consent", "CD-1", "Q23")
  Row 1  – Full question text
  Row 2  – ImportId JSON blob, e.g. {"ImportId":"QID2011"}

The ImportId (QID) is the stable identifier that links the same question
across waves even when the column name differs.  CPTC5 renamed almost every
column (Consent → Q23, Gender → Q24, …), so the QID is the only reliable
join key for cross-wave analysis.

HOW TO USE
----------
    from qid_crosswalk import QID_CROSSWALK, CANONICAL_NAME, QUESTION_TEXT

    # Get the column name for QID2011 in CPTC5:
    col = QID_CROSSWALK["QID2011"]["col_by_wave"]["CPTC5"]   # → "Q23"

    # Get the human-readable name for any QID:
    name = CANONICAL_NAME["QID2011"]                           # → "Consent"

    # Get the question text:
    text = QUESTION_TEXT["QID2011"]                            # → "Consent to Research ..."

    # Rename all columns in a loaded dataframe to canonical names:
    #   df.rename(columns=wave_to_canonical("CPTC5"), inplace=True)

HELPER FUNCTIONS
----------------
  wave_to_canonical(wave)   → dict mapping raw col names → canonical names
  canonical_to_wave(wave)   → dict mapping canonical names → raw col names
  load_wave(path, wave)     → pd.DataFrame with canonical col names, data rows only
"""

# ── QID Crosswalk ────────────────────────────────────────────────────────────
#
# Structure per entry:
#   "QID_VALUE": {
#       "canonical"   : authoritative column name used in this project,
#       "question_text": abbreviated question wording,
#       "construct"   : construct category,
#       "scale"       : measurement scale / type,
#       "col_by_wave" : { wave_key: raw_col_name_in_that_file, ... }
#   }
#
# wave keys: "CPTC8", "CPTC9", "CPTC10", "CPTC11_52", "CPTC11_55", "CPTC5"
# A wave key is absent when the question did not appear in that wave.
# CPTC11_52 and CPTC11_55 are duplicate exports of the same wave; de-duplicate
# on ResponseId before analysis.
#
# ─────────────────────────────────────────────────────────────────────────────

QID_CROSSWALK = {

    # ── Qualtrics system / metadata (camelCase ImportIds) ───────────────────
    "startDate": {
        "canonical": "StartDate",
        "question_text": "Survey start timestamp",
        "construct": "Metadata",
        "scale": "DateTime",
        "col_by_wave": {
            "CPTC8": "StartDate", "CPTC9": "StartDate", "CPTC10": "StartDate",
            "CPTC11_52": "StartDate", "CPTC11_55": "StartDate", "CPTC5": "StartDate",
        },
    },
    "endDate": {
        "canonical": "EndDate",
        "question_text": "Survey end timestamp",
        "construct": "Metadata",
        "scale": "DateTime",
        "col_by_wave": {
            "CPTC8": "EndDate", "CPTC9": "EndDate", "CPTC10": "EndDate",
            "CPTC11_52": "EndDate", "CPTC11_55": "EndDate", "CPTC5": "EndDate",
        },
    },
    "status": {
        "canonical": "Status",
        "question_text": "Response type (IP, preview, etc.)",
        "construct": "Metadata",
        "scale": "Nominal",
        "col_by_wave": {
            "CPTC8": "Status", "CPTC9": "Status", "CPTC10": "Status",
            "CPTC11_52": "Status", "CPTC11_55": "Status", "CPTC5": "Status",
        },
    },
    "ipAddress": {
        "canonical": "IPAddress",
        "question_text": "Respondent IP address",
        "construct": "Metadata",
        "scale": "Text",
        "col_by_wave": {
            "CPTC8": "IPAddress", "CPTC9": "IPAddress", "CPTC10": "IPAddress",
            "CPTC11_52": "IPAddress", "CPTC11_55": "IPAddress", "CPTC5": "IPAddress",
        },
    },
    "progress": {
        "canonical": "Progress",
        "question_text": "Completion progress (0–100)",
        "construct": "Metadata",
        "scale": "Continuous",
        "col_by_wave": {
            "CPTC8": "Progress", "CPTC9": "Progress", "CPTC10": "Progress",
            "CPTC11_52": "Progress", "CPTC11_55": "Progress", "CPTC5": "Progress",
        },
    },
    "duration": {
        "canonical": "Duration (in seconds)",
        "question_text": "Time to complete survey (seconds)",
        "construct": "Metadata",
        "scale": "Continuous",
        "col_by_wave": {
            "CPTC8": "Duration (in seconds)", "CPTC9": "Duration (in seconds)",
            "CPTC10": "Duration (in seconds)", "CPTC11_52": "Duration (in seconds)",
            "CPTC11_55": "Duration (in seconds)", "CPTC5": "Duration (in seconds)",
        },
    },
    "finished": {
        "canonical": "Finished",
        "question_text": "Whether respondent completed survey (0/1)",
        "construct": "Metadata",
        "scale": "Binary",
        "col_by_wave": {
            "CPTC8": "Finished", "CPTC9": "Finished", "CPTC10": "Finished",
            "CPTC11_52": "Finished", "CPTC11_55": "Finished", "CPTC5": "Finished",
        },
    },
    "recordedDate": {
        "canonical": "RecordedDate",
        "question_text": "Date response was recorded",
        "construct": "Metadata",
        "scale": "DateTime",
        "col_by_wave": {
            "CPTC8": "RecordedDate", "CPTC9": "RecordedDate", "CPTC10": "RecordedDate",
            "CPTC11_52": "RecordedDate", "CPTC11_55": "RecordedDate", "CPTC5": "RecordedDate",
        },
    },
    "_recordId": {
        "canonical": "ResponseId",
        "question_text": "Unique respondent identifier",
        "construct": "Metadata",
        "scale": "ID",
        "col_by_wave": {
            "CPTC8": "ResponseId", "CPTC9": "ResponseId", "CPTC10": "ResponseId",
            "CPTC11_52": "ResponseId", "CPTC11_55": "ResponseId", "CPTC5": "ResponseId",
        },
    },
    "recipientLastName": {
        "canonical": "RecipientLastName",
        "question_text": "Recipient last name (PII – typically blank)",
        "construct": "Metadata",
        "scale": "Text",
        "col_by_wave": {
            "CPTC8": "RecipientLastName", "CPTC9": "RecipientLastName",
            "CPTC10": "RecipientLastName", "CPTC11_52": "RecipientLastName",
            "CPTC11_55": "RecipientLastName", "CPTC5": "RecipientLastName",
        },
    },
    "recipientFirstName": {
        "canonical": "RecipientFirstName",
        "question_text": "Recipient first name (PII – typically blank)",
        "construct": "Metadata",
        "scale": "Text",
        "col_by_wave": {
            "CPTC8": "RecipientFirstName", "CPTC9": "RecipientFirstName",
            "CPTC10": "RecipientFirstName", "CPTC11_52": "RecipientFirstName",
            "CPTC11_55": "RecipientFirstName", "CPTC5": "RecipientFirstName",
        },
    },
    "recipientEmail": {
        "canonical": "RecipientEmail",
        "question_text": "Recipient email (PII – typically blank)",
        "construct": "Metadata",
        "scale": "Text",
        "col_by_wave": {
            "CPTC8": "RecipientEmail", "CPTC9": "RecipientEmail",
            "CPTC10": "RecipientEmail", "CPTC11_52": "RecipientEmail",
            "CPTC11_55": "RecipientEmail", "CPTC5": "RecipientEmail",
        },
    },
    "externalDataReference": {
        "canonical": "ExternalReference",
        "question_text": "External data reference field",
        "construct": "Metadata",
        "scale": "Text",
        "col_by_wave": {
            "CPTC8": "ExternalReference", "CPTC9": "ExternalReference",
            "CPTC10": "ExternalReference", "CPTC11_52": "ExternalReference",
            "CPTC11_55": "ExternalReference", "CPTC5": "ExternalReference",
        },
    },
    "locationLatitude": {
        "canonical": "LocationLatitude",
        "question_text": "Respondent location latitude",
        "construct": "Metadata",
        "scale": "Continuous",
        "col_by_wave": {
            "CPTC8": "LocationLatitude", "CPTC9": "LocationLatitude",
            "CPTC10": "LocationLatitude", "CPTC11_52": "LocationLatitude",
            "CPTC11_55": "LocationLatitude", "CPTC5": "LocationLatitude",
        },
    },
    "locationLongitude": {
        "canonical": "LocationLongitude",
        "question_text": "Respondent location longitude",
        "construct": "Metadata",
        "scale": "Continuous",
        "col_by_wave": {
            "CPTC8": "LocationLongitude", "CPTC9": "LocationLongitude",
            "CPTC10": "LocationLongitude", "CPTC11_52": "LocationLongitude",
            "CPTC11_55": "LocationLongitude", "CPTC5": "LocationLongitude",
        },
    },
    "distributionChannel": {
        "canonical": "DistributionChannel",
        "question_text": "How survey was distributed",
        "construct": "Metadata",
        "scale": "Nominal",
        "col_by_wave": {
            "CPTC8": "DistributionChannel", "CPTC9": "DistributionChannel",
            "CPTC10": "DistributionChannel", "CPTC11_52": "DistributionChannel",
            "CPTC11_55": "DistributionChannel", "CPTC5": "DistributionChannel",
        },
    },
    "userLanguage": {
        "canonical": "UserLanguage",
        "question_text": "Respondent language setting",
        "construct": "Metadata",
        "scale": "Nominal",
        "col_by_wave": {
            "CPTC8": "UserLanguage", "CPTC9": "UserLanguage", "CPTC10": "UserLanguage",
            "CPTC11_52": "UserLanguage", "CPTC11_55": "UserLanguage", "CPTC5": "UserLanguage",
        },
    },

    # ── Survey questions (uppercase QID) ────────────────────────────────────

    # Consent
    "QID2011": {
        "canonical": "Consent",
        "question_text": "Consent to Research – do you consent to participate?",
        "construct": "Consent",
        "scale": "Nominal (Yes / No)",
        "col_by_wave": {
            "CPTC8": "Consent", "CPTC9": "Consent", "CPTC10": "Consent",
            "CPTC11_52": "Consent", "CPTC11_55": "Consent", "CPTC5": "Q23",
        },
    },

    # Demographics
    "QID2024": {
        "canonical": "Team ID",
        "question_text": "What was your team number at this year's finals?",
        "construct": "Demographic Controls",
        "scale": "Nominal",
        "col_by_wave": {
            "CPTC8": "Team ID", "CPTC9": "Team ID", "CPTC10": "Team ID",
            "CPTC11_52": "Team ID", "CPTC11_55": "Team ID", "CPTC5": "Team ID",
            # absent in CPTC5
        },
    },
    "QID2012": {
        "canonical": "Gender",
        "question_text": "Please select your gender",
        "construct": "Demographic Controls",
        "scale": "Nominal (categorical)",
        "col_by_wave": {
            "CPTC8": "Gender", "CPTC9": "Gender", "CPTC10": "Gender",
            "CPTC11_52": "Gender", "CPTC11_55": "Gender", "CPTC5": "Q24",
        },
    },
    "QID2013": {
        "canonical": "Age",
        "question_text": "Please select your age group",
        "construct": "Demographic Controls",
        "scale": "Ordinal",
        "col_by_wave": {
            "CPTC8": "Age", "CPTC9": "Age", "CPTC10": "Age",
            "CPTC11_52": "Age", "CPTC11_55": "Age", "CPTC5": "Q25",
        },
    },
    "QID2014": {
        "canonical": "Formal Education",
        "question_text": "How many years of formal education in cybersecurity?",
        "construct": "Demographic Controls",
        "scale": "Ordinal / Continuous",
        "col_by_wave": {
            "CPTC8": "Formal Education", "CPTC9": "Formal Education",
            "CPTC10": "Formal Education", "CPTC11_52": "Formal Education",
            "CPTC11_55": "Formal Education", "CPTC5": "Q26",
        },
    },
    "QID2015": {
        "canonical": "Degree Status",
        "question_text": "Please select your current degree status",
        "construct": "Demographic Controls",
        "scale": "Ordinal",
        "col_by_wave": {
            "CPTC8": "Degree Status", "CPTC9": "Degree Status", "CPTC10": "Degree Status",
            "CPTC11_52": "Degree Status", "CPTC11_55": "Degree Status", "CPTC5": "Q27",
        },
    },
    "QID2016_TEXT": {
        "canonical": "Major",
        "question_text": "My major is: (open text)",
        "construct": "Demographic Controls",
        "scale": "Text",
        "col_by_wave": {
            "CPTC8": "Major", "CPTC9": "Major", "CPTC10": "Major",
            "CPTC11_52": "Major", "CPTC11_55": "Major", "CPTC5": "Q28",
        },
    },

    # Experience & Confidence battery (QID2017 sub-items)
    "QID2017_1": {
        "canonical": "Experience_1",
        "question_text": "How many security competitions have you participated in (before this one)?",
        "construct": "Experience & Confidence",
        "scale": "Ordinal count",
        "col_by_wave": {
            "CPTC8": "Experience_1", "CPTC9": "Experience_1", "CPTC10": "Experience_1",
            "CPTC11_52": "Experience_1", "CPTC11_55": "Experience_1", "CPTC5": "Q29_1",
        },
    },
    "QID2017_4": {
        "canonical": "Experience_2",
        "question_text": "How confident are you that you currently have the skills to be an effective penetration tester? (0–10)",
        "construct": "Experience & Confidence",
        "scale": "Likert 0–10",
        "col_by_wave": {
            "CPTC8": "Experience_2", "CPTC9": "Experience_2", "CPTC10": "Experience_2",
            "CPTC11_52": "Experience_2", "CPTC11_55": "Experience_2", "CPTC5": "Q29_4",
        },
    },
    "QID2017_5": {
        "canonical": "Experience_3",
        "question_text": "How many years of penetration testing experience do you have?",
        "construct": "Experience & Confidence",
        "scale": "Ordinal / Continuous",
        "col_by_wave": {
            "CPTC8": "Experience_3", "CPTC9": "Experience_3", "CPTC10": "Experience_3",
            "CPTC11_52": "Experience_3", "CPTC11_55": "Experience_3", "CPTC5": "Q29_5",
        },
    },
    # CPTC5-only experience sub-items
    "QID2017_6": {
        "canonical": "Experience_4",
        "question_text": "How many years do you feel it takes to become an effective penetration tester?",
        "construct": "Experience & Confidence",
        "scale": "Ordinal / Continuous",
        "col_by_wave": {
            "CPTC5": "Q29_6",
        },
    },
    "QID2017_7": {
        "canonical": "Experience_5",
        "question_text": "How many hours/week do you spend on required cybersecurity exercises?",
        "construct": "Experience & Confidence",
        "scale": "Continuous",
        "col_by_wave": {
            "CPTC5": "Q29_7",
        },
    },
    "QID2017_8": {
        "canonical": "Experience_6",
        "question_text": "How many hours/week do you spend on voluntary (not required) cybersecurity exercises?",
        "construct": "Experience & Confidence",
        "scale": "Continuous",
        "col_by_wave": {
            "CPTC5": "Q29_8",
        },
    },

    # Career intent (CPTC5 only)
    "QID2018": {
        "canonical": "Career Intent",
        "question_text": "Do you plan to pursue cybersecurity as a career?",
        "construct": "Demographic Controls",
        "scale": "Nominal (Yes / No)",
        "col_by_wave": {
            "CPTC5": "Q30",
        },
    },

    # Differing Abilities / Self-categorization
    "QID2019_0": {
        "canonical": "Differing abilities_1",
        "question_text": "How likely are you to self-categorize according to this definition? (definition 1 – disability/neurodiversity)",
        "construct": "Perceived Cognitive Diversity — Self-Categorization",
        "scale": "Likert 1–5",
        "col_by_wave": {
            "CPTC8": "Differing abilities_1", "CPTC9": "Differing abilities_1",
            "CPTC10": "Differing abilities_1", "CPTC11_52": "Differing abilities_1",
            "CPTC11_55": "Differing abilities_1",
        },
    },
    "QID2019_11": {
        "canonical": "Differing abilities_2",
        "question_text": "How likely are you to self-categorize according to this definition? (definition 2)",
        "construct": "Perceived Cognitive Diversity — Self-Categorization",
        "scale": "Likert 1–5",
        "col_by_wave": {
            "CPTC8": "Differing abilities_2", "CPTC9": "Differing abilities_2",
            "CPTC10": "Differing abilities_2", "CPTC11_52": "Differing abilities_2",
            "CPTC11_55": "Differing abilities_2",
        },
    },
    "QID2019_12": {
        "canonical": "Differing abilities_3",
        "question_text": "How likely are you to self-categorize according to this definition? (definition 3)",
        "construct": "Perceived Cognitive Diversity — Self-Categorization",
        "scale": "Likert 1–5",
        "col_by_wave": {
            "CPTC8": "Differing abilities_3", "CPTC9": "Differing abilities_3",
            "CPTC10": "Differing abilities_3", "CPTC11_52": "Differing abilities_3",
            "CPTC11_55": "Differing abilities_3",
        },
    },

    # CPTC5 Competition NPS
    "QID2019_NPS_GROUP": {
        "canonical": "Q31_NPS_GROUP",
        "question_text": "NPS group classification (Detractor / Passive / Promoter) for competition recommendation",
        "construct": "Competition NPS",
        "scale": "Nominal (derived)",
        "col_by_wave": {
            "CPTC5": "Q31_NPS_GROUP",
        },
    },
    "QID2019": {
        "canonical": "Competition NPS",
        "question_text": "How likely are you to recommend CPTC to a friend or colleague? (0–10)",
        "construct": "Competition NPS",
        "scale": "NPS 0–10",
        "col_by_wave": {
            "CPTC5": "Q31",
        },
    },

    # Cognitive Diversity – CD items
    # NOTE: Numeric codes are non-contiguous: 1=very large, 2=large, 3=somewhat large,
    #       4=moderate, 17=somewhat small, 18=small, 19=very small.
    # Recode to 7-point scale (7=very large … 1=very small) before analysis.
    "QID1": {
        "canonical": "CD-1",
        "question_text": "To what extent do the members of your team differ in their way of thinking?",
        "construct": "Perceived Cognitive Diversity — CD Items",
        "scale": "Likert 1–5 (non-contiguous codes; see recode note)",
        "col_by_wave": {
            "CPTC8": "CD-1", "CPTC9": "CD-1", "CPTC10": "CD-1",
            "CPTC11_52": "CD-1", "CPTC11_55": "CD-1",
        },
    },
    "QID2022": {
        "canonical": "CD-2",
        "question_text": "To what extent do the members of your team differ in their knowledge and skills?",
        "construct": "Perceived Cognitive Diversity — CD Items",
        "scale": "Likert 1–5 (non-contiguous codes; see recode note)",
        "col_by_wave": {
            "CPTC8": "CD-2", "CPTC9": "CD-2", "CPTC10": "CD-2",
            "CPTC11_52": "CD-2", "CPTC11_55": "CD-2",
        },
    },
    "QID2021": {
        "canonical": "CD-3",
        "question_text": "To what extent do the members of your team differ in how they view the world?",
        "construct": "Perceived Cognitive Diversity — CD Items",
        "scale": "Likert 1–5 (non-contiguous codes; see recode note)",
        "col_by_wave": {
            "CPTC8": "CD-3", "CPTC9": "CD-3", "CPTC10": "CD-3",
            "CPTC11_52": "CD-3", "CPTC11_55": "CD-3",
        },
    },
    "QID2023": {
        "canonical": "CD-4",
        "question_text": "To what extent do the members of your team differ in their beliefs about what is right and wrong?",
        "construct": "Perceived Cognitive Diversity — CD Items",
        "scale": "Likert 1–5 (non-contiguous codes; see recode note)",
        "col_by_wave": {
            "CPTC8": "CD-4", "CPTC9": "CD-4", "CPTC10": "CD-4",
            "CPTC11_52": "CD-4", "CPTC11_55": "CD-4",
        },
    },

    # CPTC5 CD-1 equivalent (slider / rank format — different instrument)
    "QID2021_1": {
        "canonical": "Q33_1",
        "question_text": "Team differs in way of thinking — choice 1 (To a very large extent)",
        "construct": "Perceived Cognitive Diversity — CD Items",
        "scale": "Rank / nominal (CPTC5 format)",
        "col_by_wave": {
            "CPTC5": "Q33_1",
        },
    },
    "QID2021_2": {
        "canonical": "Q33_2",
        "question_text": "Team differs in way of thinking — choice 2",
        "construct": "Perceived Cognitive Diversity — CD Items",
        "scale": "Rank / nominal (CPTC5 format)",
        "col_by_wave": {
            "CPTC5": "Q33_2",
        },
    },
    "QID2021_3": {
        "canonical": "Q33_3",
        "question_text": "Team differs in way of thinking — choice 3",
        "construct": "Perceived Cognitive Diversity — CD Items",
        "scale": "Rank / nominal (CPTC5 format)",
        "col_by_wave": {
            "CPTC5": "Q33_3",
        },
    },
    "QID2021_4": {
        "canonical": "Q33_4",
        "question_text": "Team differs in way of thinking — choice 4",
        "construct": "Perceived Cognitive Diversity — CD Items",
        "scale": "Rank / nominal (CPTC5 format)",
        "col_by_wave": {
            "CPTC5": "Q33_4",
        },
    },

    # Team Cohesion – Open Communication (OC) items
    "QID2025": {
        "canonical": "OC-1",
        "question_text": 'Agree/disagree: "My Coach and Captain keep me informed."',
        "construct": "Team Cohesion — Coach Communication",
        "scale": "Likert 1–5",
        "col_by_wave": {
            "CPTC8": "OC-1", "CPTC9": "OC-1", "CPTC10": "OC-1",
            "CPTC11_52": "OC-1", "CPTC11_55": "OC-1",
        },
    },
    "QID2026": {
        "canonical": "OC-2",
        "question_text": 'Agree/disagree: "Sharing of knowledge is encouraged by my team in actions and not only in words."',
        "construct": "Team Cohesion — Knowledge Sharing",
        "scale": "Likert 1–5",
        "col_by_wave": {
            "CPTC8": "OC-2", "CPTC9": "OC-2", "CPTC10": "OC-2",
            "CPTC11_52": "OC-2", "CPTC11_55": "OC-2",
        },
    },
    "QID2027": {
        "canonical": "OC-3",
        "question_text": 'Agree/disagree: "We are continuously encouraged to bring new knowledge into the team."',
        "construct": "Team Cohesion — Knowledge Sharing",
        "scale": "Likert 1–5",
        "col_by_wave": {
            "CPTC8": "OC-3", "CPTC9": "OC-3", "CPTC10": "OC-3",
            "CPTC11_52": "OC-3", "CPTC11_55": "OC-3",
        },
    },
    "QID2028": {
        "canonical": "OC-4",
        "question_text": 'Agree/disagree: "We are encouraged to say what we think even if it means disagreeing with the Coach or Captain."',
        "construct": "Team Cohesion — Openness",
        "scale": "Likert 1–5",
        "col_by_wave": {
            "CPTC8": "OC-4", "CPTC9": "OC-4", "CPTC10": "OC-4",
            "CPTC11_52": "OC-4", "CPTC11_55": "OC-4",
        },
    },
    "QID2029": {
        "canonical": "OC-5",
        "question_text": 'Agree/disagree: "Open communication is characteristic of the team as a whole."',
        "construct": "Team Cohesion — Openness",
        "scale": "Likert 1–5",
        "col_by_wave": {
            "CPTC8": "OC-5", "CPTC9": "OC-5", "CPTC10": "OC-5",
            "CPTC11_52": "OC-5", "CPTC11_55": "OC-5",
        },
    },

    # AI Authority by Phase (QID2033 sub-items)
    "QID2033_11": {
        "canonical": "Q24_1",
        "question_text": "Authority granted to AI: Planning phase (define scope and threat models) — scale 1–5",
        "construct": "AI Authority by Phase — Planning",
        "scale": "Likert 1–5",
        "col_by_wave": {
            "CPTC10": "Q24_1", "CPTC11_52": "Q24_1", "CPTC11_55": "Q24_1",
        },
    },
    "QID2033_12": {
        "canonical": "Q24_2",
        "question_text": "Authority granted to AI: Scanning phase (enumerate potential vulnerabilities) — scale 1–5",
        "construct": "AI Authority by Phase — Scanning",
        "scale": "Likert 1–5",
        "col_by_wave": {
            "CPTC10": "Q24_2", "CPTC11_52": "Q24_2", "CPTC11_55": "Q24_2",
        },
    },
    "QID2033_13": {
        "canonical": "Q24_3",
        "question_text": "Authority granted to AI: Execution phase (emulate attacker / exploit vulnerabilities) — scale 1–5",
        "construct": "AI Authority by Phase — Execution",
        "scale": "Likert 1–5",
        "col_by_wave": {
            "CPTC10": "Q24_3", "CPTC11_52": "Q24_3", "CPTC11_55": "Q24_3",
        },
    },
    "QID2033_15": {
        "canonical": "Q24_4",
        "question_text": "Authority granted to AI: Analysis phase (consider business impacts of exploits) — scale 1–5",
        "construct": "AI Authority by Phase — Analysis",
        "scale": "Likert 1–5",
        "col_by_wave": {
            "CPTC10": "Q24_4", "CPTC11_52": "Q24_4", "CPTC11_55": "Q24_4",
        },
    },
    "QID2033_16": {
        "canonical": "Q24_5",
        "question_text": "Authority granted to AI: Output phase (pentest reports / actionable insights) — scale 1–5",
        "construct": "AI Authority by Phase — Output",
        "scale": "Likert 1–5",
        "col_by_wave": {
            "CPTC10": "Q24_5", "CPTC11_52": "Q24_5", "CPTC11_55": "Q24_5",
        },
    },

    # AI Teammate Value – NPS-style (CPTC11 only)
    "QID2036_NPS_GROUP": {
        "canonical": "Q27_NPS_GROUP",
        "question_text": "NPS group (Detractor/Passive/Promoter): AI as teammate for TECHNICAL FINDINGS",
        "construct": "AI Teammate Value — Technical Findings",
        "scale": "Nominal (derived from NPS)",
        "col_by_wave": {
            "CPTC11_52": "Q27_NPS_GROUP", "CPTC11_55": "Q27_NPS_GROUP",
        },
    },
    "QID2036": {
        "canonical": "Q27",
        "question_text": "How much would you recommend AI as a useful teammate for TECHNICAL FINDINGS? (0–10)",
        "construct": "AI Teammate Value — Technical Findings",
        "scale": "NPS 0–10",
        "col_by_wave": {
            "CPTC11_52": "Q27", "CPTC11_55": "Q27",
        },
    },
    "QID2037_NPS_GROUP": {
        "canonical": "Q28_NPS_GROUP",
        "question_text": "NPS group (Detractor/Passive/Promoter): AI as teammate for REPORT WRITING",
        "construct": "AI Teammate Value — Report Writing",
        "scale": "Nominal (derived from NPS)",
        "col_by_wave": {
            "CPTC11_52": "Q28_NPS_GROUP", "CPTC11_55": "Q28_NPS_GROUP",
        },
    },
    "QID2037": {
        "canonical": "Q28",
        "question_text": "How much would you recommend AI as a useful teammate for REPORT WRITING? (0–10)",
        "construct": "AI Teammate Value — Report Writing",
        "scale": "NPS 0–10",
        "col_by_wave": {
            "CPTC11_52": "Q28", "CPTC11_55": "Q28",
        },
    },
    "QID2038_NPS_GROUP": {
        "canonical": "Q29_NPS_GROUP",
        "question_text": "NPS group (Detractor/Passive/Promoter): AI as teammate for PRESENTATION",
        "construct": "AI Teammate Value — Presentation",
        "scale": "Nominal (derived from NPS)",
        "col_by_wave": {
            "CPTC11_52": "Q29_NPS_GROUP", "CPTC11_55": "Q29_NPS_GROUP",
        },
    },
    "QID2038": {
        "canonical": "Q29",
        "question_text": "How much would you recommend AI as a useful teammate for PRESENTATION? (0–10)",
        "construct": "AI Teammate Value — Presentation",
        "scale": "NPS 0–10",
        "col_by_wave": {
            "CPTC11_52": "Q29", "CPTC11_55": "Q29",
        },
    },

    # Qualitative AI experience (CPTC11 only)
    "QID2039_TEXT": {
        "canonical": "Q30_AI_Qual",
        "question_text": "Please describe your use of AI. What worked for you? What didn't work for you?",
        "construct": "Qualitative AI Experience",
        "scale": "Free text",
        "col_by_wave": {
            "CPTC11_52": "Q30", "CPTC11_55": "Q30",
        },
    },

    # Scenario-Based Cognition (CPTC5 only)
    "QID2_TEXT": {
        "canonical": "Scenario_Situation",
        "question_text": "Briefly describe a specific security situation encountered (attack plan formulation)",
        "construct": "Scenario Cognition — Situation Description",
        "scale": "Free text",
        "col_by_wave": {
            "CPTC5": "Q3",
        },
    },
    "QID3_1": {
        "canonical": "Prepared_Environment",
        "question_text": "How prepared to resolve situation: understanding the environment (0–100 slider)",
        "construct": "Scenario Cognition — Preparedness",
        "scale": "Continuous 0–100",
        "col_by_wave": {
            "CPTC5": "Q4_1",
        },
    },
    "QID3_2": {
        "canonical": "Prepared_Rules",
        "question_text": "How prepared to resolve situation: understanding the competition rules (0–100 slider)",
        "construct": "Scenario Cognition — Preparedness",
        "scale": "Continuous 0–100",
        "col_by_wave": {
            "CPTC5": "Q4_2",
        },
    },
    "QID3_3": {
        "canonical": "Prepared_Role",
        "question_text": "How prepared to resolve situation: understanding your role in the team (0–100 slider)",
        "construct": "Scenario Cognition — Preparedness",
        "scale": "Continuous 0–100",
        "col_by_wave": {
            "CPTC5": "Q4_3",
        },
    },
    "QID3_4": {
        "canonical": "Prepared_Actions",
        "question_text": "How prepared to resolve situation: understanding the actions required (0–100 slider)",
        "construct": "Scenario Cognition — Preparedness",
        "scale": "Continuous 0–100",
        "col_by_wave": {
            "CPTC5": "Q4_4",
        },
    },
    "QID3_5": {
        "canonical": "Prepared_Communication",
        "question_text": "How prepared to resolve situation: understanding how to communicate professionally (0–100 slider)",
        "construct": "Scenario Cognition — Preparedness",
        "scale": "Continuous 0–100",
        "col_by_wave": {
            "CPTC5": "Q4_5",
        },
    },
    "QID3_6": {
        "canonical": "Prepared_Ethics",
        "question_text": "How prepared to resolve situation: understanding the ethical implications (0–100 slider)",
        "construct": "Scenario Cognition — Preparedness",
        "scale": "Continuous 0–100",
        "col_by_wave": {
            "CPTC5": "Q4_6",
        },
    },
    "QID4_TEXT": {
        "canonical": "Scenario_Observations",
        "question_text": "What observations did you make about the situation? How did you identify the problem?",
        "construct": "Scenario Cognition — Observations (Scanning)",
        "scale": "Free text",
        "col_by_wave": {
            "CPTC5": "Q5",
        },
    },
    "QID5_TEXT": {
        "canonical": "Scenario_StateAssessment",
        "question_text": "How did you determine the actual system state from your observations?",
        "construct": "Scenario Cognition — State Assessment",
        "scale": "Free text",
        "col_by_wave": {
            "CPTC5": "Q6",
        },
    },
    "QID6_TEXT": {
        "canonical": "Scenario_Options",
        "question_text": "What options did you have to act on the system state?",
        "construct": "Scenario Cognition — Option Generation",
        "scale": "Free text",
        "col_by_wave": {
            "CPTC5": "Q7",
        },
    },
    "QID7_TEXT": {
        "canonical": "Scenario_OptionEval",
        "question_text": "How did you evaluate the consequences of the different options?",
        "construct": "Scenario Cognition — Option Evaluation",
        "scale": "Free text",
        "col_by_wave": {
            "CPTC5": "Q8",
        },
    },
    "QID8_TEXT": {
        "canonical": "Scenario_OptionSelect",
        "question_text": "How did you select an option to achieve the desired system state?",
        "construct": "Scenario Cognition — Option Selection",
        "scale": "Free text",
        "col_by_wave": {
            "CPTC5": "Q9",
        },
    },
    "QID8_TEXT_98d09e12885144e18ddbbbc2ParTopics": {
        "canonical": "Scenario_OptionSelect_ParentTopics",
        "question_text": "NLP-derived parent topic tags for Q9 (option selection narrative)",
        "construct": "Scenario Cognition — Option Selection (NLP derived)",
        "scale": "Derived / Text",
        "col_by_wave": {
            "CPTC5": "Q9 - Parent Topics",
        },
    },
    "QID8_TEXT_98d09e12885144e18ddbbbc2Topics": {
        "canonical": "Scenario_OptionSelect_Topics",
        "question_text": "NLP-derived topic tags for Q9 (option selection narrative)",
        "construct": "Scenario Cognition — Option Selection (NLP derived)",
        "scale": "Derived / Text",
        "col_by_wave": {
            "CPTC5": "Q9 - Topics",
        },
    },
    "QID10_TEXT": {
        "canonical": "Scenario_TargetState",
        "question_text": "What was the target state of the system?",
        "construct": "Scenario Cognition — Target State",
        "scale": "Free text",
        "col_by_wave": {
            "CPTC5": "Q11",
        },
    },
    "QID11_TEXT": {
        "canonical": "Scenario_TaskPlanning",
        "question_text": "What tasks did you need to plan for?",
        "construct": "Scenario Cognition — Task Planning",
        "scale": "Free text",
        "col_by_wave": {
            "CPTC5": "Q12",
        },
    },
    "QID2003_TEXT": {
        "canonical": "Scenario_ProcedurePlanning",
        "question_text": "What procedures did you plan to complete the tasks?",
        "construct": "Scenario Cognition — Procedure Planning",
        "scale": "Free text",
        "col_by_wave": {
            "CPTC5": "Q15",
        },
    },
    "QID2004_TEXT": {
        "canonical": "Scenario_ActionsTaken",
        "question_text": "What actions did you take?",
        "construct": "Scenario Cognition — Actions Taken",
        "scale": "Free text",
        "col_by_wave": {
            "CPTC5": "Q16",
        },
    },
    "QID2005": {
        "canonical": "Scenario_Iterate",
        "question_text": "Would you like to describe another security situation you encountered?",
        "construct": "Scenario Cognition — Iteration",
        "scale": "Nominal (Yes / No)",
        "col_by_wave": {
            "CPTC5": "Q17",
        },
    },
}


# ── Convenience lookups ───────────────────────────────────────────────────────

CANONICAL_NAME = {qid: v["canonical"] for qid, v in QID_CROSSWALK.items()}
QUESTION_TEXT  = {qid: v["question_text"] for qid, v in QID_CROSSWALK.items()}
CONSTRUCT      = {qid: v["construct"] for qid, v in QID_CROSSWALK.items()}
SCALE          = {qid: v["scale"] for qid, v in QID_CROSSWALK.items()}


def wave_to_canonical(wave: str) -> dict:
    """
    Return a dict mapping raw column names (as they appear in the CSV for
    `wave`) to canonical names.

    Example
    -------
    >>> wave_to_canonical("CPTC5")
    {"Q23": "Consent", "Q24": "Gender", ..., "Q9": "Scenario_OptionSelect", ...}
    """
    mapping = {}
    for qid, entry in QID_CROSSWALK.items():
        raw_col = entry["col_by_wave"].get(wave)
        if raw_col:
            mapping[raw_col] = entry["canonical"]
    return mapping


def canonical_to_wave(wave: str) -> dict:
    """
    Return a dict mapping canonical names to raw column names for `wave`.
    Columns absent in that wave are not included.
    """
    return {v: k for k, v in wave_to_canonical(wave).items()}


def load_wave(path: str, wave: str, use_text: bool = True):
    """
    Load a CPTC survey CSV, skip the three-row header block, and rename
    all columns to their canonical names.

    Parameters
    ----------
    path      : path to the CSV file
    wave      : one of "CPTC8", "CPTC9", "CPTC10", "CPTC11_52",
                "CPTC11_55", "CPTC5"
    use_text  : if True, read values as text (Text_ exports);
                set False for Nums_ exports

    Returns
    -------
    pd.DataFrame  with canonical column names, data only (header rows stripped)
    """
    import pandas as pd
    df = pd.read_csv(path, encoding="utf-8-sig", skiprows=[1, 2], dtype=str)
    df.rename(columns=wave_to_canonical(wave), inplace=True)
    df["_wave"] = wave
    return df


# ── CD recode map (non-contiguous Qualtrics choice IDs → 7-point scale) ──────
# Apply to CD-1, CD-2, CD-3, CD-4 columns loaded from Nums_ files.
# Higher recoded value = greater perceived cognitive diversity.
CD_RECODE = {
    "1":  7,   # very large extent
    "2":  6,   # large extent
    "3":  5,   # somewhat large extent
    "4":  4,   # moderate extent
    "17": 3,   # somewhat small extent
    "18": 2,   # small extent
    "19": 1,   # very small extent
}

CD_COLUMNS = ["CD-1", "CD-2", "CD-3", "CD-4"]


if __name__ == "__main__":
    # Print a compact crosswalk table to stdout for quick inspection
    waves = ["CPTC8", "CPTC9", "CPTC10", "CPTC11_52", "CPTC11_55", "CPTC5"]
    header = f"{'QID':<45} {'Canonical':<30} " + " ".join(f"{w:<12}" for w in waves)
    print(header)
    print("-" * len(header))
    for qid, entry in QID_CROSSWALK.items():
        cols = [entry["col_by_wave"].get(w, "—") for w in waves]
        row = f"  {qid:<43} {entry['canonical']:<30} " + " ".join(f"{c:<12}" for c in cols)
        print(row)
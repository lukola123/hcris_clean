"""
Worksheet/line/column -> named-financial-variable crosswalk.

IMPORTANT — READ BEFORE TRUSTING ANY ENTRY BELOW:
Every entry in CROSSWALK is a PLACEHOLDER seeded from commonly-cited HCRIS
line items in the published hospital-finance literature (e.g. net income on
Worksheet G-3, cash position on Worksheet G). None of these (wksht_cd,
line_num, clmn_num) addresses have been confirmed against an actual
downloaded HCRIS extract, and CMS is known to renumber specific lines
between cost-report form versions (2552-96 vs 2552-10) and occasionally
within a form version across years.

Do not feed a variable into clean.build_panel() until profile.py has been
run against the real fiscal-year extract you're using and its output
confirms the (wksht_cd, line_num, clmn_num) address actually contains what
you expect (e.g. numeric values in a plausible dollar range, for the right
subset of providers). Flip `confirmed` to True only after doing that, and
record the fiscal year(s)/form version(s) that confirmation covered in
`confirmed_for`.
"""

CROSSWALK = {
    "net_income": {
        "wksht_cd": "G300000", "line_num": 2900, "clmn_num": 100,
        "description": "Net income (worksheet G-3, excess of revenues over expenses)",
        "confirmed": False, "confirmed_for": [],
    },
    "total_operating_expenses": {
        "wksht_cd": "G300000", "line_num": 400, "clmn_num": 100,
        "description": "Total operating expenses (worksheet G-3)",
        "confirmed": False, "confirmed_for": [],
    },
    "net_patient_revenue": {
        "wksht_cd": "G300000", "line_num": 100, "clmn_num": 100,
        "description": "Net patient revenue (worksheet G-3)",
        "confirmed": False, "confirmed_for": [],
    },
    "cash_and_equivalents": {
        "wksht_cd": "G000000", "line_num": 100, "clmn_num": 100,
        "description": "Cash on hand and in banks (worksheet G, balance sheet)",
        "confirmed": False, "confirmed_for": [],
    },
    "current_assets": {
        "wksht_cd": "G000000", "line_num": 2100, "clmn_num": 100,
        "description": "Total current assets (worksheet G, balance sheet)",
        "confirmed": False, "confirmed_for": [],
    },
    "current_liabilities": {
        "wksht_cd": "G000000", "line_num": 4500, "clmn_num": 100,
        "description": "Total current liabilities (worksheet G, balance sheet)",
        "confirmed": False, "confirmed_for": [],
    },
    "total_beds": {
        "wksht_cd": "S300001", "line_num": 100, "clmn_num": 200,
        "description": "Total hospital beds (worksheet S-3, Part I)",
        "confirmed": False, "confirmed_for": [],
    },
}


def unconfirmed_variables():
    return [name for name, spec in CROSSWALK.items() if not spec["confirmed"]]


def lookup(nmrc_df, wksht_cd, line_num, clmn_num):
    """Returns the NMRC rows matching one crosswalk address, across all reports."""
    return nmrc_df[
        (nmrc_df["WKSHT_CD"] == wksht_cd)
        & (nmrc_df["LINE_NUM"] == line_num)
        & (nmrc_df["CLMN_NUM"] == clmn_num)
    ]

"""
Build a tidy provider x fiscal-year financial panel from a loaded HCRIS
triplet, and derive standard hospital financial-distress indicators from it.
"""

import pandas as pd
from .crosswalk import CROSSWALK, lookup

# HCRIS commonly carries more than one report per provider-fiscal-year (an
# original submission plus later amendments/settlements sharing overlapping
# fiscal periods). RPT_STUS_CD marks each report's status. This default
# priority (lower = preferred) is a DOCUMENTED ASSUMPTION, not yet confirmed
# against real data — profile.py prints the actual RPT_STUS_CD distribution
# specifically so this can be checked before trusting it. Adjust to match
# what your extract's own RPT_STUS_CD values and CMS's current HCRIS record
# layout actually document.
DEFAULT_STATUS_PRIORITY = {"S": 0, "R": 1, "T": 2}  # Settled, Reopened, aTtempted... CONFIRM


def dedupe_to_one_report_per_provider_fy(rpt_df, status_priority=None):
    """
    Collapses RPT to one row per (PRVDR_NUM, FY_BGN_DT, FY_END_DT), keeping
    the row whose RPT_STUS_CD sorts first under status_priority (unknown
    codes sort last, not silently dropped) and, as a tiebreak, the latest
    FI_CREAT_DT. Returns the deduped RPT frame plus the set of RPT_REC_NUM
    values that were dropped, so a caller can sanity-check how much overlap
    existed before trusting the result.
    """
    status_priority = status_priority or DEFAULT_STATUS_PRIORITY
    df = rpt_df.copy()
    df["_status_rank"] = df["RPT_STUS_CD"].map(status_priority).fillna(999)
    df = df.sort_values(["_status_rank", "FI_CREAT_DT"], ascending=[True, False])
    kept = df.drop_duplicates(subset=["PRVDR_NUM", "FY_BGN_DT", "FY_END_DT"], keep="first")
    dropped_ids = set(rpt_df["RPT_REC_NUM"]) - set(kept["RPT_REC_NUM"])
    kept = kept.drop(columns=["_status_rank"])
    print(f"dedupe_to_one_report_per_provider_fy: {len(rpt_df):,} reports -> "
          f"{len(kept):,} kept, {len(dropped_ids):,} dropped as duplicate/superseded")
    return kept, dropped_ids


def extract_variables(nmrc_df, crosswalk=None, only_confirmed=False):
    """
    Pivots the requested crosswalk variables out of the long NMRC file into
    a wide frame keyed by RPT_REC_NUM (one column per variable).

    only_confirmed=True restricts to crosswalk entries with confirmed=True —
    use this once you've actually run profile.py and vetted the addresses;
    the default (False) pulls everything so you can inspect unconfirmed
    variables too, but they should not be trusted for analysis yet.
    """
    crosswalk = crosswalk or CROSSWALK
    frames = []
    for name, spec in crosswalk.items():
        if only_confirmed and not spec["confirmed"]:
            continue
        rows = lookup(nmrc_df, spec["wksht_cd"], spec["line_num"], spec["clmn_num"])
        s = rows.set_index("RPT_REC_NUM")["ITM_VAL_NUM"].rename(name)
        frames.append(s)
    if not frames:
        raise ValueError(
            "No crosswalk variables selected — did you mean only_confirmed=False, "
            "or has nothing in crosswalk.py been confirmed yet via profile.py?"
        )
    wide = pd.concat(frames, axis=1)
    return wide.reset_index()


def build_panel(rpt_df, nmrc_df, crosswalk=None, only_confirmed=False, status_priority=None):
    """
    Full assembly: dedupe RPT to one report per provider-fiscal-year, pull
    the requested financial variables via the crosswalk, and join them onto
    the provider/fiscal-year identifiers. Returns one row per
    (PRVDR_NUM, FY_BGN_DT, FY_END_DT).
    """
    rpt_deduped, dropped_ids = dedupe_to_one_report_per_provider_fy(rpt_df, status_priority)
    values = extract_variables(nmrc_df, crosswalk, only_confirmed)

    panel = rpt_deduped.merge(values, on="RPT_REC_NUM", how="left")
    panel["fiscal_year"] = pd.to_datetime(panel["FY_END_DT"], errors="coerce").dt.year
    print(f"build_panel: {len(panel):,} provider-fiscal-year rows, "
          f"{panel['PRVDR_NUM'].nunique():,} distinct providers, "
          f"years {panel['fiscal_year'].min()}-{panel['fiscal_year'].max()}")
    return panel


def add_distress_indicators(panel):
    """
    Adds standard hospital financial-distress ratios used in the rural-
    hospital-finance literature (cross-check definitions against Flex
    Monitoring Team's published financial-indicator methodology before
    treating these as final — ratio *definitions* are fairly standard, but
    the exact HCRIS line items feeding them still depend on crosswalk.py
    being confirmed).

      operating_margin     = net_income / net_patient_revenue
      current_ratio        = current_assets / current_liabilities
      days_cash_on_hand    = cash_and_equivalents / (total_operating_expenses / 365)

    Divide-by-zero and missing inputs produce NaN, not an error or a silent
    zero — a hospital with a real distress signal (e.g. zero current
    liabilities reported) should be visibly NaN/flagged, not indistinguishable
    from a hospital with genuinely healthy ratios.
    """
    panel = panel.copy()

    def safe_div(a, b):
        return a / b.replace({0: pd.NA})

    if {"net_income", "net_patient_revenue"}.issubset(panel.columns):
        panel["operating_margin"] = safe_div(panel["net_income"], panel["net_patient_revenue"])
    if {"current_assets", "current_liabilities"}.issubset(panel.columns):
        panel["current_ratio"] = safe_div(panel["current_assets"], panel["current_liabilities"])
    if {"cash_and_equivalents", "total_operating_expenses"}.issubset(panel.columns):
        daily_opex = panel["total_operating_expenses"] / 365
        panel["days_cash_on_hand"] = safe_div(panel["cash_and_equivalents"], daily_opex)

    return panel

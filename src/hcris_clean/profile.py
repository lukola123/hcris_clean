"""
Diagnostic-only pass over one HCRIS extract — run BEFORE trusting crosswalk.py.

This module makes no changes and derives no output data — it only reports
what's actually in the file so a human can confirm or correct crosswalk.py's
worksheet/line/column addresses for the specific form/year in hand.
"""

from .crosswalk import CROSSWALK, lookup


def top_worksheet_lines(nmrc_df, n=25):
    """
    Most frequently populated (WKSHT_CD, LINE_NUM, CLMN_NUM) addresses —
    orients you to which worksheets/lines actually carry data in this
    extract before you go hunting for a specific one.
    """
    counts = (
        nmrc_df.groupby(["WKSHT_CD", "LINE_NUM", "CLMN_NUM"])
        .size()
        .sort_values(ascending=False)
        .head(n)
    )
    return counts


def check_crosswalk_addresses(nmrc_df, crosswalk=CROSSWALK):
    """
    For every variable in crosswalk.py, reports how many reports actually
    have a value at that address, plus min/median/max — so an obviously
    wrong address (zero matches, or a value range that can't be a dollar
    figure) is visible immediately rather than silently producing an
    all-NaN column downstream.
    """
    results = {}
    for name, spec in crosswalk.items():
        rows = lookup(nmrc_df, spec["wksht_cd"], spec["line_num"], spec["clmn_num"])
        n = len(rows)
        summary = {
            "wksht_cd": spec["wksht_cd"], "line_num": spec["line_num"],
            "clmn_num": spec["clmn_num"], "n_reports_with_value": n,
            "confirmed": spec["confirmed"],
        }
        if n:
            vals = rows["ITM_VAL_NUM"]
            summary.update(min=vals.min(), median=vals.median(), max=vals.max())
        results[name] = summary
    return results


def profile_extract(rpt_df, alpha_df, nmrc_df):
    print(f"\n{'='*70}\nHCRIS EXTRACT PROFILE\n{'='*70}")
    print(f"Reports (RPT):  {len(rpt_df):,} rows, "
          f"{rpt_df['PRVDR_NUM'].nunique():,} distinct provider numbers")
    print(f"ALPHA cells:    {len(alpha_df):,} rows")
    print(f"NMRC cells:     {len(nmrc_df):,} rows")

    print(f"\nTop {25} most-populated (worksheet, line, column) addresses in NMRC "
          f"(orientation only, not the crosswalk check):")
    for (wksht, line, clmn), cnt in top_worksheet_lines(nmrc_df).items():
        print(f"    {wksht:>10} line={line:<6} col={clmn:<6} {cnt:>10,} reports")

    print(f"\nCrosswalk address check (crosswalk.py) — confirm each variable "
          f"has a plausible n_reports_with_value and value range before "
          f"trusting it, and before flipping 'confirmed' to True in crosswalk.py:")
    for name, summary in check_crosswalk_addresses(nmrc_df).items():
        print(f"    {name:28s} {summary}")

    print(f"\nRPT_STUS_CD value counts (report status — confirm which codes mean "
          f"'as-submitted' vs 'settled/final' before deciding which to keep; "
          f"mixing both in one panel double-counts provider-years):")
    print(rpt_df["RPT_STUS_CD"].value_counts(dropna=False).to_string())

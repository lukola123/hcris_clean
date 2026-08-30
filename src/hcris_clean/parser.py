"""
Read the three flat files that make up one HCRIS extract.

HCRIS ships each fiscal-year/form extract as three headerless, comma- or
pipe-delimited files sharing a common naming stem:

    *_RPT.CSV    — one row per submitted cost report ("report control" file):
                   RPT_REC_NUM, PRVDR_CTRL_TYPE_CD, PRVDR_NUM, NPI, RPT_STUS_CD,
                   FY_BGN_DT, FY_END_DT, PROC_DT, INITL_RPT_SW, LAST_RPT_SW,
                   TRNSMTL_NUM, FI_NUM, ADR_VNDR_CD, FI_CREAT_DT, UTIL_CD,
                   NPR_DT, SPEC_IND, FI_RCPT_DT
    *_ALPHA.CSV  — free-text worksheet cells, "long" format:
                   RPT_REC_NUM, WKSHT_CD, LINE_NUM, CLMN_NUM, ALPHNMRC_ITM_TXT
    *_NMRC.CSV   — numeric worksheet cells, "long" format:
                   RPT_REC_NUM, WKSHT_CD, LINE_NUM, CLMN_NUM, ITM_VAL_NUM

The "long" (worksheet, line, column) addressing is the source of most of the
real work in this package: a financial figure like "net income" isn't a named
column, it's a specific (WKSHT_CD, LINE_NUM, CLMN_NUM) cell that has to be
looked up via crosswalk.py, and that address can differ between cost-report
form versions (2552-96 vs 2552-10) and has been known to shift for individual
line items across years. See profile.py — DO NOT trust crosswalk.py's mapping
for a new form/year until profile.py's output confirms it against the real
file.

This module deliberately does NOT hardcode exact filenames (e.g. whether a
given year's zip names the numeric file "*_NMRC.CSV" or "*_NUMERIC.CSV") —
it discovers the three files by suffix pattern and fails loudly, listing what
it found, if it can't identify exactly one of each.
"""

import glob
import os
import pandas as pd

RPT_COLUMNS = [
    "RPT_REC_NUM", "PRVDR_CTRL_TYPE_CD", "PRVDR_NUM", "NPI", "RPT_STUS_CD",
    "FY_BGN_DT", "FY_END_DT", "PROC_DT", "INITL_RPT_SW", "LAST_RPT_SW",
    "TRNSMTL_NUM", "FI_NUM", "ADR_VNDR_CD", "FI_CREAT_DT", "UTIL_CD",
    "NPR_DT", "SPEC_IND", "FI_RCPT_DT",
]
ALPHA_COLUMNS = ["RPT_REC_NUM", "WKSHT_CD", "LINE_NUM", "CLMN_NUM", "ALPHNMRC_ITM_TXT"]
NMRC_COLUMNS = ["RPT_REC_NUM", "WKSHT_CD", "LINE_NUM", "CLMN_NUM", "ITM_VAL_NUM"]

_SUFFIX_CANDIDATES = {
    "rpt": ["_RPT.CSV", "_RPT.csv"],
    "alpha": ["_ALPHA.CSV", "_alpha.csv"],
    "nmrc": ["_NMRC.CSV", "_nmrc.csv", "_NUMERIC.CSV", "_numeric.csv"],
}


def find_triplet_files(extract_dir):
    """
    Returns {"rpt": path, "alpha": path, "nmrc": path}. Raises FileNotFoundError
    with the full directory listing if any of the three isn't found exactly
    once — a loud, inspectable failure instead of silently parsing nothing.
    """
    found = {}
    for kind, suffixes in _SUFFIX_CANDIDATES.items():
        matches = []
        for suffix in suffixes:
            matches.extend(glob.glob(os.path.join(extract_dir, f"*{suffix}")))
        matches = sorted(set(matches))
        if len(matches) != 1:
            listing = os.listdir(extract_dir)
            raise FileNotFoundError(
                f"Expected exactly one '{kind}' file (suffix in {suffixes}) in "
                f"{extract_dir}, found {len(matches)}: {matches}.\n"
                f"Full directory contents: {listing}\n"
                f"CMS may use a different naming convention for this form/year — "
                f"inspect the directory and extend _SUFFIX_CANDIDATES rather than "
                f"guessing."
            )
        found[kind] = matches[0]
    return found


def _read_flat(path, columns, dtype=None):
    df = pd.read_csv(path, header=None, names=columns, dtype=dtype, low_memory=False)
    if len(df.columns) != len(columns):
        raise ValueError(
            f"{path}: expected {len(columns)} columns ({columns}), "
            f"got {len(df.columns)}. The record layout for this file may have "
            f"changed — do not proceed without re-confirming column order "
            f"against CMS's current HCRIS record-layout documentation."
        )
    return df


def load_hcris_triplet(extract_dir):
    """
    Loads and returns (rpt_df, alpha_df, nmrc_df) for one extract directory.
    RPT_REC_NUM is read as a string in all three frames (it's a join key, not
    a quantity — parsing it as int risks silent precision/leading-zero bugs
    on a merge key).
    """
    paths = find_triplet_files(extract_dir)
    rpt = _read_flat(paths["rpt"], RPT_COLUMNS, dtype={"RPT_REC_NUM": str, "PRVDR_NUM": str})
    alpha = _read_flat(paths["alpha"], ALPHA_COLUMNS, dtype={"RPT_REC_NUM": str})
    nmrc = _read_flat(paths["nmrc"], NMRC_COLUMNS, dtype={"RPT_REC_NUM": str})
    print(f"Loaded RPT: {len(rpt):,} rows | ALPHA: {len(alpha):,} rows | NMRC: {len(nmrc):,} rows")
    return rpt, alpha, nmrc

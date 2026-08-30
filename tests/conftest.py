import pytest
import pandas as pd

from hcris_clean.parser import RPT_COLUMNS, ALPHA_COLUMNS, NMRC_COLUMNS
from hcris_clean.crosswalk import CROSSWALK


def _rpt_row(rec_num, prvdr, fy_bgn, fy_end, stus="S", fi_creat="2023-01-01"):
    return {
        "RPT_REC_NUM": rec_num, "PRVDR_CTRL_TYPE_CD": "1", "PRVDR_NUM": prvdr,
        "NPI": "", "RPT_STUS_CD": stus, "FY_BGN_DT": fy_bgn, "FY_END_DT": fy_end,
        "PROC_DT": fy_end, "INITL_RPT_SW": "Y", "LAST_RPT_SW": "Y",
        "TRNSMTL_NUM": "1", "FI_NUM": "00001", "ADR_VNDR_CD": "",
        "FI_CREAT_DT": fi_creat, "UTIL_CD": "F", "NPR_DT": fy_end,
        "SPEC_IND": "", "FI_RCPT_DT": fy_end,
    }


@pytest.fixture
def synthetic_extract_dir(tmp_path):
    """
    Builds a small, realistic-shaped synthetic HCRIS extract (RPT/ALPHA/NMRC
    files) covering: two providers, two fiscal years, and one duplicate
    provider-fiscal-year (an original 'R' report superseded by a 'S' settled
    report) to exercise dedupe_to_one_report_per_provider_fy().
    """
    rpt_rows = [
        _rpt_row("1001", "100001", "2022-01-01", "2022-12-31", stus="S", fi_creat="2023-03-01"),
        _rpt_row("1002", "100001", "2023-01-01", "2023-12-31", stus="S", fi_creat="2024-03-01"),
        # duplicate provider-fiscal-year for 100002/2022: superseded 'R' + final 'S'
        _rpt_row("2001", "100002", "2022-01-01", "2022-12-31", stus="R", fi_creat="2023-02-01"),
        _rpt_row("2002", "100002", "2022-01-01", "2022-12-31", stus="S", fi_creat="2023-05-01"),
    ]
    rpt_df = pd.DataFrame(rpt_rows, columns=RPT_COLUMNS)

    # Financial figures, deliberately simple round numbers for easy assertion.
    financials = {
        "1001": dict(net_income=1_000_000, total_operating_expenses=9_000_000,
                     net_patient_revenue=10_000_000, cash_and_equivalents=900_000,
                     current_assets=2_000_000, current_liabilities=1_000_000, total_beds=25),
        "1002": dict(net_income=-500_000, total_operating_expenses=9_500_000,
                     net_patient_revenue=9_000_000, cash_and_equivalents=100_000,
                     current_assets=1_000_000, current_liabilities=1_500_000, total_beds=25),
        "2001": dict(net_income=200_000, total_operating_expenses=5_000_000,
                     net_patient_revenue=5_200_000, cash_and_equivalents=400_000,
                     current_assets=800_000, current_liabilities=400_000, total_beds=15),
        "2002": dict(net_income=250_000, total_operating_expenses=5_050_000,
                     net_patient_revenue=5_300_000, cash_and_equivalents=450_000,
                     current_assets=850_000, current_liabilities=400_000, total_beds=15),
    }

    nmrc_rows = []
    for rec_num, values in financials.items():
        for var_name, val in values.items():
            spec = CROSSWALK[var_name]
            nmrc_rows.append({
                "RPT_REC_NUM": rec_num, "WKSHT_CD": spec["wksht_cd"],
                "LINE_NUM": spec["line_num"], "CLMN_NUM": spec["clmn_num"],
                "ITM_VAL_NUM": val,
            })
    nmrc_df = pd.DataFrame(nmrc_rows, columns=NMRC_COLUMNS)

    alpha_df = pd.DataFrame(
        [{"RPT_REC_NUM": "1001", "WKSHT_CD": "S200001", "LINE_NUM": 100,
          "CLMN_NUM": 100, "ALPHNMRC_ITM_TXT": "SAMPLE HOSPITAL A"}],
        columns=ALPHA_COLUMNS,
    )

    extract_dir = tmp_path / "synthetic_fy_extract"
    extract_dir.mkdir()
    rpt_df.to_csv(extract_dir / "SYNTH_RPT.CSV", header=False, index=False)
    alpha_df.to_csv(extract_dir / "SYNTH_ALPHA.CSV", header=False, index=False)
    nmrc_df.to_csv(extract_dir / "SYNTH_NMRC.CSV", header=False, index=False)

    return str(extract_dir)

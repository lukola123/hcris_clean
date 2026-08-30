import pytest

from hcris_clean.parser import load_hcris_triplet
from hcris_clean.clean import (
    dedupe_to_one_report_per_provider_fy,
    build_panel,
    add_distress_indicators,
)


@pytest.fixture
def triplet(synthetic_extract_dir):
    return load_hcris_triplet(synthetic_extract_dir)


def test_dedupe_drops_superseded_report(triplet):
    rpt, _, _ = triplet
    kept, dropped_ids = dedupe_to_one_report_per_provider_fy(rpt)
    # 4 raw reports -> 3 provider-fiscal-years (100002/2022 had 2 reports)
    assert len(kept) == 3
    assert dropped_ids == {"2001"}  # the 'R' (superseded) report, not the 'S' (settled) one
    assert "2002" in set(kept["RPT_REC_NUM"])


def test_build_panel_and_indicators(triplet):
    rpt, _, nmrc = triplet
    panel = build_panel(rpt, nmrc)
    assert len(panel) == 3

    panel = add_distress_indicators(panel)
    row_1002 = panel.loc[panel["RPT_REC_NUM"] == "1002"].iloc[0]
    # net_income=-500,000 / net_patient_revenue=9,000,000
    assert row_1002["operating_margin"] == pytest.approx(-500_000 / 9_000_000)

    row_1001 = panel.loc[panel["RPT_REC_NUM"] == "1001"].iloc[0]
    assert row_1001["current_ratio"] == pytest.approx(2_000_000 / 1_000_000)
    assert row_1001["days_cash_on_hand"] == pytest.approx(900_000 / (9_000_000 / 365))

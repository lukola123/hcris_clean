from hcris_clean.parser import load_hcris_triplet
from hcris_clean.profile import profile_extract, check_crosswalk_addresses


def test_profile_extract_runs_without_error(synthetic_extract_dir, capsys):
    rpt, alpha, nmrc = load_hcris_triplet(synthetic_extract_dir)
    profile_extract(rpt, alpha, nmrc)  # should not raise
    captured = capsys.readouterr()
    assert "HCRIS EXTRACT PROFILE" in captured.out


def test_check_crosswalk_addresses_finds_seeded_variables(synthetic_extract_dir):
    _, _, nmrc = load_hcris_triplet(synthetic_extract_dir)
    results = check_crosswalk_addresses(nmrc)
    assert results["net_income"]["n_reports_with_value"] == 4
    assert results["net_income"]["min"] <= results["net_income"]["max"]

import pandas as pd

from hcris_clean.parser import load_hcris_triplet, find_triplet_files


def test_find_triplet_files(synthetic_extract_dir):
    paths = find_triplet_files(synthetic_extract_dir)
    assert set(paths.keys()) == {"rpt", "alpha", "nmrc"}
    for p in paths.values():
        assert p.endswith(".CSV")


def test_load_hcris_triplet_shapes(synthetic_extract_dir):
    rpt, alpha, nmrc = load_hcris_triplet(synthetic_extract_dir)
    assert len(rpt) == 4
    assert len(alpha) == 1
    assert len(nmrc) == 4 * 7  # 4 reports x 7 financial variables each
    # kept as string, not coerced to int (join keys shouldn't be numeric)
    assert not pd.api.types.is_integer_dtype(rpt["RPT_REC_NUM"])
    assert rpt["RPT_REC_NUM"].iloc[0] == "1001"

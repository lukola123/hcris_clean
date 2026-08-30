# Contributing to hcris-clean

Issues and pull requests are welcome — this project explicitly needs
outside confirmation of crosswalk addresses across cost-report form
versions and years, which is exactly the kind of contribution that's hard
for one person to fully cover alone.

## Development setup

```bash
git clone https://github.com/lukola123/hcris_clean.git
cd hcris_clean
pip install -e ".[dev]"
pytest
```

## Before opening a PR

- Add or update tests under `tests/` — new crosswalk entries or parsing
  behavior should come with a synthetic-fixture test (see
  `tests/conftest.py`), not just a manual check against a real download
  (real HCRIS files are large and shouldn't be required to run the test
  suite).
- If you're confirming a crosswalk address against a real extract, say
  which form version and fiscal year(s) you checked, and flip that entry's
  `confirmed` field in `crosswalk.py` with `confirmed_for` listing them.
- Run `pytest` locally before pushing; CI runs the same suite.

## Reporting a wrong crosswalk address

Open an issue with: the form version and fiscal year, the
`(wksht_cd, line_num, clmn_num)` you expected vs. what `profile.py` shows,
and — if possible — a link to the CMS worksheet instructions or record
layout confirming the correct address.

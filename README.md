# hcris-clean

Parse and clean raw CMS Healthcare Cost Report Information System (HCRIS)
flat files into tidy, analysis-ready hospital financial panels — with an
explicit, testable crosswalk from worksheet/line/column addresses to named
financial variables, and a profiling step that empirically confirms that
crosswalk against real data before it's trusted.

## Why this exists

HCRIS is the primary public source of individual hospital financial data in
the U.S. (cost, revenue, balance-sheet, and utilization detail self-reported
via Medicare cost reports), but the raw files are unfriendly to work with
directly:

- Each fiscal-year extract ships as three separate, headerless flat files
  (`*_RPT.CSV`, `*_ALPHA.CSV`, `*_NMRC.CSV`) joined by an opaque report ID.
- Financial figures live in a "long" worksheet/line/column addressing scheme,
  not named columns — e.g. net income isn't a column called `net_income`,
  it's a specific cell on Worksheet G-3.
- Those addresses differ between cost-report form versions (1996 vs 2010)
  and have shifted across years for individual line items.
- A single provider-fiscal-year can appear more than once (original
  submission, amendment, settlement) and naive concatenation double-counts.

`hcris-clean` handles the mechanical parsing and joins, keeps the
worksheet/line/column crosswalk as an explicit, inspectable, testable
artifact rather than baked-in magic numbers, and — critically — ships a
`profile` step that reports what's actually in a given extract so the
crosswalk can be confirmed (or corrected) per form version/year rather than
assumed. See `src/hcris_clean/crosswalk.py`'s module docstring: every
shipped crosswalk entry is currently a documented placeholder pending that
confirmation.

## Install

```bash
pip install -e ".[dev]"
```

## Quickstart

```python
from hcris_clean import download, parser, profile, clean

# 1. Download + extract one fiscal year's HCRIS zip (copy the exact .zip URL
#    from CMS's "Cost Reports by Fiscal Year" page for the form/year you want)
extract_dir = download.fetch_fiscal_year(
    zip_url="https://www.cms.gov/.../hosp10_2023.zip",
    work_dir="./data/raw",
)

# 2. Load the RPT/ALPHA/NMRC triplet
rpt, alpha, nmrc = parser.load_hcris_triplet(extract_dir)

# 3. Profile BEFORE trusting the crosswalk — inspect the printed output
profile.profile_extract(rpt, alpha, nmrc)

# 4. Build the panel and derive distress indicators
panel = clean.build_panel(rpt, nmrc)
panel = clean.add_distress_indicators(panel)
```

## Data source

Raw HCRIS extracts: CMS, [Cost Reports](https://www.cms.gov/data-research/statistics-trends-and-reports/cost-reports)
/ [Cost Reports by Fiscal Year](https://www.cms.gov/data-research/statistics-trends-and-reports/cost-reports/cost-reports-fiscal-year).
Free technical assistance from [ResDAC](https://resdac.org/) for researchers
working with CMS data, including HCRIS.

## Related work

[`imccart/HCRIS`](https://github.com/imccart/HCRIS) and
[`jfangmeier/hcris-cost-reports`](https://github.com/jfangmeier/hcris-cost-reports)
both parse HCRIS flat files and are worth reviewing before relying on this
package — part of preparing this project for JOSS submission is articulating
concretely how it differs (language/ecosystem, form-version coverage, the
crosswalk-confirmation workflow, distress-indicator layer, and test
coverage) rather than duplicating existing tools. Fill this section in
honestly once that comparison has actually been done against the real repos,
not assumed.

## Status

Alpha. The financial-variable crosswalk (`src/hcris_clean/crosswalk.py`) is
seeded with commonly-cited line items from the hospital-finance literature
but **none of it is confirmed yet** — run `profile.profile_extract()` against
a real downloaded extract and update `crosswalk.py` accordingly before using
this for actual analysis.

## Citing CMS data

Per CMS's data-use terms, cite the source explicitly in any derived work,
e.g.: "Source: Centers for Medicare & Medicaid Services, Healthcare Cost
Report Information System (HCRIS), [fiscal year(s) used]."

## License

MIT — see `LICENSE`.

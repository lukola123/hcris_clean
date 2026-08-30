"""
hcris_clean — parse and clean raw CMS HCRIS cost-report flat files.

Public API (see each module's docstring for the reasoning behind it):
    download.fetch_fiscal_year(...)   — pull a fiscal year's raw HCRIS zip from CMS
    parser.load_hcris_triplet(...)    — read the RPT/ALPHA/NMRC files for one extract
    crosswalk.CROSSWALK                — worksheet/line/column -> named-variable map
    profile.profile_extract(...)      — diagnostic pass BEFORE trusting the crosswalk
    clean.build_panel(...)            — long triplet -> tidy provider x fiscal-year panel
    clean.add_distress_indicators(...) — standard financial-distress ratios
"""

from . import download, parser, crosswalk, profile, clean

__all__ = ["download", "parser", "crosswalk", "profile", "clean"]
__version__ = "0.1.0"

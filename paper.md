---
title: 'hcris-clean: A Python package for parsing and cleaning CMS Healthcare Cost Report Information System (HCRIS) data'
tags:
  - Python
  - health economics
  - hospital finance
  - public health
  - rural health
authors:
  - name: Abiola Olayinka
    orcid: 0009-0008-7217-2991
    affiliation: 1
affiliations:
  - name: Independent Researcher
    index: 1
date: 30 August 2026
bibliography: paper.bib
---

# Summary

`hcris-clean` is a Python package for turning raw Healthcare Cost Report
Information System (HCRIS) flat files — the Centers for Medicare & Medicaid
Services' (CMS) primary public source of individual hospital financial
data — into tidy, analysis-ready panels. Each fiscal-year HCRIS extract is
distributed as three headerless files joined by an opaque report identifier,
with financial line items addressed by a worksheet/line/column scheme that
differs across cost-report form versions and has shifted for individual
items across years. `hcris-clean` provides (1) a parser for the raw
three-file extract, (2) an explicit, version-controlled crosswalk from
worksheet/line/column addresses to named financial variables, (3) a
profiling step that empirically checks that crosswalk against a real
extract before it is trusted, (4) deduplication of overlapping
provider-fiscal-year report submissions, and (5) a small set of standard
hospital financial-distress indicators (operating margin, current ratio,
days cash on hand) built on top of the cleaned panel.

# Statement of need

HCRIS is the primary public source of individual hospital financial data in
the United States, and underlies published research on hospital financial
distress, rural hospital closures, and Medicare payment policy. REPLACE —
this claim needs specific peer-reviewed citations before submission (see
the note in `paper.bib`); do not submit with this sentence uncited.

Existing open-source tools for reading HCRIS exist and are actively
maintained [@imccart_hcris; @fangmeier_hcris], but neither documents a step
that empirically confirms a worksheet/line/column crosswalk address against
a real extract before that address is used to extract a value — a real risk
given that CMS has renumbered specific lines both across cost-report form
versions and, at times, within a form version across years (see State of
the field for the specific comparison). `hcris-clean` is built around
making that confirmation step explicit and mandatory rather than assumed,
while intentionally covering a narrower range of cost-report forms than the
most comprehensive existing tool. Intended users are health services
researchers, rural health policy analysts, and journalists working with
hospital-level financial data who need to know which parts of a crosswalk
they can trust for the specific form version and fiscal year they are
using, rather than inheriting an unverified one.

# State of the field

Two actively maintained open-source tools already parse and organize HCRIS
data. `imccart/HCRIS` [@imccart_hcris] extracts and combines HCRIS data
across three cost-report reporting eras — PPS-based reporting (1985–1999),
Form 2552-96 (1998–2011), and Form 2552-10 (2010–2025) — in parallel R and
Python implementations, and applies a multi-tier deduplication algorithm
that sums, selects, or apportions overlapping provider-fiscal-year report
submissions according to how much of the fiscal year each one covers.
`jfangmeier/hcris-cost-reports` [@fangmeier_hcris] targets Form 2552-10
only (2010–present), automates quarterly data refresh via a scheduled
GitHub Actions workflow, converts fiscal-year reports to synthetic
calendar-year values by apportioning across year boundaries (a feature its
own documentation labels experimental), and drives a public Shiny
dashboard for per-hospital profiles; it computes two margin-based ratios
(operating margin and excess margin) directly in its output.

Neither tool documents an empirical step that confirms a worksheet/line/
column address actually contains the expected data in a given extract
before that address is relied on. `imccart/HCRIS`'s variable locations for
the 1996 and 2010 forms are hardcoded directly in its extraction scripts
(an external crosswalk file is used only for the older, pre-1996 PPS-era
form); `jfangmeier/hcris-cost-reports` joins against an external lookup
spreadsheet without a comparable validation step. `hcris-clean` differs by
keeping every crosswalk entry as an explicit, individually-confirmable
record (`confirmed` / `confirmed_for` in `crosswalk.py`) and shipping a
profiling step (`profile.py`) whose output against a real extract is what
confirms or corrects an address, rather than treating the crosswalk as
correct by construction.

This comes with a real, stated trade-off rather than an unqualified
improvement: `hcris-clean` currently targets Form 2552-96 and Form 2552-10
only, not the pre-1996 PPS-based reporting that `imccart/HCRIS` also
covers, and its deduplication rule (a single status-priority ranking with
a most-recent-report tiebreak) is simpler than `imccart/HCRIS`'s
day-span-based tiered aggregation, which sums, selects, or prorates
overlapping reports depending on fiscal-year coverage. What `hcris-clean`
adds beyond either existing tool is a small set of standard liquidity and
solvency indicators (current ratio, days cash on hand) alongside operating
margin, computed directly on the cleaned panel — and, more centrally, the
confirm-before-trust workflow described above.

# Software design

REPLACE — an explanation of the trade-offs weighed and why (e.g. why the
crosswalk is a plain Python dict with an explicit `confirmed` flag rather
than an external spreadsheet or a fully automated validator; why profiling
is a separate, non-mutating step rather than folded into cleaning; why
deduplication uses a single status-priority rule rather than the more
elaborate day-span apportionment `imccart/HCRIS` uses, and what that
trade-off costs and buys).

# Research impact statement

REPLACE — JOSS requires evidence of realized impact (citation in a
paper/preprint, documented external use) or credible near-term
significance. Aspirational statements are not sufficient. Do not write
this section until `hcris-clean` has actually been used in something.

# AI usage disclosure

REPLACE — JOSS requires transparent disclosure of any generative-AI use in
the software's creation, documentation, or this paper's authoring. Write
this accurately once, covering the whole project, not per-section.

# Acknowledgements

REPLACE — funding sources, data-access assistance (e.g. ResDAC), or
contributors to acknowledge.

# References

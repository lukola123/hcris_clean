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

REPLACE — write this section honestly once related work has actually been
reviewed. It should establish: (a) why HCRIS matters (it underlies published
research on hospital financial distress, rural hospital closures, and
Medicare payment policy — cite specific papers here, not just an assertion),
(b) that existing open tools for reading HCRIS exist
[@imccart_hcris; @fangmeier_hcris] and what gap remains (e.g. a
Python-native tool with an explicit, tested, and empirically-confirmable
crosswalk plus a built-in distress-indicator layer, if that is in fact true
once those tools are actually reviewed — do not assert this without
checking), and (c) who the intended users are (health services researchers,
rural health policy analysts, journalists).

# Acknowledgements

REPLACE — funding sources, data-access assistance (e.g. ResDAC), or
contributors to acknowledge.

# References

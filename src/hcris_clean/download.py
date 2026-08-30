"""
Download raw HCRIS fiscal-year extracts from CMS.

CMS publishes one zip file per fiscal year per cost-report form family, linked
from the "Cost Reports by Fiscal Year" page:
    https://www.cms.gov/data-research/statistics-trends-and-reports/cost-reports/cost-reports-fiscal-year

DELIBERATELY NOT hardcoding those per-year zip URLs here: CMS has changed its
page/URL structure before, and a scraper that guesses a URL pattern will
silently break or (worse) silently fetch the wrong year's file the next time
CMS reorganizes the page. Instead, this module takes the exact zip URL as an
argument — copy it from the fiscal-year page for the year/form you want — and
does the download + extraction + light validation. If you want to automate
the "which years exist" discovery step too, that's a good candidate for a
small, separately-tested scraper function once the page structure is
confirmed against the live site rather than assumed here.
"""

import os
import zipfile
import hashlib
import requests

CHUNK_SIZE = 1 << 20  # 1 MB


def download_file(url, dest_path, timeout=60):
    """Streams url to dest_path. Returns dest_path. Raises on non-200 status."""
    with requests.get(url, stream=True, timeout=timeout) as resp:
        resp.raise_for_status()
        os.makedirs(os.path.dirname(os.path.abspath(dest_path)), exist_ok=True)
        with open(dest_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)
    return dest_path


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_zip(zip_path, extract_dir):
    """
    Extracts zip_path into extract_dir and returns the list of extracted file
    paths. Does not assume specific member filenames — HCRIS zip contents are
    named per form/year (e.g. HOSP10_2023_RPT.CSV vs a different convention
    for the 2552-96 form) and should be discovered, not guessed (see
    parser.find_triplet_files).
    """
    os.makedirs(extract_dir, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(extract_dir)
        names = zf.namelist()
    return [os.path.join(extract_dir, n) for n in names]


def fetch_fiscal_year(zip_url, work_dir, label=None):
    """
    Downloads and extracts one fiscal-year HCRIS zip.

    zip_url : the exact .zip URL copied from CMS's fiscal-year cost-report
              page for the form/year you want.
    work_dir: local directory to hold the downloaded zip and its extracted
              contents (kept as a real intermediate artifact, not a temp file
              that vanishes on error — makes a failed/partial run inspectable).
    label   : optional short name (e.g. "hosp_2010_fy2023") used to name the
              downloaded zip and extraction subfolder; inferred from the URL
              if omitted.
    """
    label = label or os.path.splitext(os.path.basename(zip_url.split("?")[0]))[0]
    zip_path = os.path.join(work_dir, f"{label}.zip")
    extract_dir = os.path.join(work_dir, label)

    print(f"Downloading {zip_url} -> {zip_path}")
    download_file(zip_url, zip_path)
    print(f"    sha256: {sha256_of(zip_path)}  (record this for provenance/reproducibility)")

    print(f"Extracting -> {extract_dir}")
    members = extract_zip(zip_path, extract_dir)
    print(f"    {len(members)} member file(s) extracted")
    return extract_dir

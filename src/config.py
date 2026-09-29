"""Shared paths and constants for the MGT-403 daycare project.

Everything that PS4, PS5, and the final project must agree on lives here so the
three deliverables cannot drift apart. Import it; do not re-declare these
values in notebooks.

    from src.config import RAW, YEARS, ID_DTYPES
"""

from pathlib import Path

# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent

DATA = ROOT / "data"
RAW = DATA / "raw"                    # immutable downloads, gitignored
CROSSWALKS = DATA / "crosswalks"      # course-provided, committed
INTERIM = DATA / "interim"            # disposable intermediates
PROCESSED = DATA / "processed"        # built analysis datasets

FIGURES = ROOT / "output" / "figures"
TABLES = ROOT / "output" / "tables"

NDCP_XLSX = RAW / "ndcp" / "NDCP2022.xlsx"
CPI_MONTHLY = RAW / "cpi" / "cpi_u_cuur0000sa0_monthly.txt"
OEWS_CROSSWALK = CROSSWALKS / "county_oews_crosswalk.csv"

# --------------------------------------------------------------------------
# Sample definition
# --------------------------------------------------------------------------
YEARS = range(2015, 2023)             # 2015-2022 inclusive
BASE_YEAR = 2022                      # constant-dollar base for CPI-U deflation

# Metro analysis sample: keep counties whose OEWS area code begins with "00",
# drop the remaining nonmetro codes. Applied once, in build_sample.py, so PS4
# and PS5 share a county set (see assignment PS4 §1).
METRO_AREA_PREFIX = "00"

# --------------------------------------------------------------------------
# Identifier dtypes
# --------------------------------------------------------------------------
# County FIPS is 5 chars (state 2 + county 3); OEWS area codes are 7 chars.
# Both are zero-padded STRINGS. Read them as integers and the leading zeros
# vanish silently -- the join then fails with no error, just missing rows.
# Pass this to every read_csv / read_excel that touches an identifier.
ID_DTYPES = {
    "county_fips": str,
    "County_FIPS_Code": str,          # NDCP's spelling
    "oews_area": str,
    "area": str,                      # OEWS raw files' spelling
    "AREA": str,
    "state_fips": str,
}

FIPS_WIDTH = 5
OEWS_AREA_WIDTH = 7

# --------------------------------------------------------------------------
# PS4 §4 — CCDF voucher hypothesis test
# --------------------------------------------------------------------------
# Monthly voucher amounts for center-based preschool care, NOMINAL dollars.
# NDCP prices are full-time WEEKLY; the assignment specifies 4.33 weeks/month.
WEEKS_PER_MONTH = 4.33
CCDF_VOUCHER_NOMINAL = {2015: 473.0, 2022: 706.0}

ALPHA = 0.05                          # test level, also drives the 95% CIs


def ensure_dirs() -> None:
    """Create the working dirs if a fresh clone is missing them.

    git cannot track empty directories, and data/raw/ is gitignored, so a
    clone arrives without the download folders. Run this before downloading.
    """
    raw_subdirs = (RAW / "ndcp", RAW / "cpi", RAW / "oews", RAW / "acs")
    for d in (*raw_subdirs, INTERIM, PROCESSED, FIGURES, TABLES):
        d.mkdir(parents=True, exist_ok=True)

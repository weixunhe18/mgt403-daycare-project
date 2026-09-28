"""Convert nominal dollars to constant 2022 dollars using CPI-U.

Series: CUUR0000SA0 (All Urban Consumers, U.S. city average, all items),
ANNUAL AVERAGES -- not a single month, not seasonally adjusted. Download from
bls.gov/cpi and save the file to data/raw/cpi/ so the numbers are auditable;
do not retype them from a webpage into a dict here without keeping the source.

Used by PS4 §3 (price trends), PS5 §5 (wages and rents), and the project.
Deflate every dollar series with this one function so the deliverables can't
end up on different bases.
"""

import pandas as pd

from .config import BASE_YEAR, CPI_CSV


def load_cpi(path=CPI_CSV) -> pd.Series:
    """Return annual-average CPI-U indexed by year (int)."""
    # TODO: read the saved BLS file and return a year -> index Series covering
    # at least YEARS. Assert no years are missing before returning.
    raise NotImplementedError


def deflators(base_year: int = BASE_YEAR) -> pd.Series:
    """Return year -> multiplier that converts nominal to base-year dollars.

    The multiplier for year t is CPI[base] / CPI[t]; it equals 1.0 in the base
    year, which is a cheap sanity check that you built it the right way up.
    """
    raise NotImplementedError


def to_real(df: pd.DataFrame, cols, year_col: str = "year",
            base_year: int = BASE_YEAR) -> pd.DataFrame:
    """Add real-dollar counterparts of `cols`, suffixed `_real`.

    Keep the nominal columns alongside. PS4 §4 tests the 2015 voucher against
    2015 prices in NOMINAL terms (both figures are given nominal), while §3
    plots real trends -- you need both in the same frame.
    """
    raise NotImplementedError

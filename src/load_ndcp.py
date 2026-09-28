"""Load the NDCP county-level childcare price workbook.

Scope: read NDCP2022.xlsx off disk and return a tidy frame. No filtering, no
deflation, no analysis -- those belong in build_sample.py and deflate.py.

Before writing this, open Appendix C of the NDCP Technical Report (Sept 2024)
and save it next to the workbook. The column names are terse abbreviations;
you need the data dictionary to pick the right ones. Watch for:

  - center-based ("day care center") vs. family/home-based providers
  - median vs. 75th-percentile price columns
  - the three age groups (infant / toddler / preschool)
  - prices are full-time WEEKLY, nominal dollars

Record in DECISIONS.md which columns you mapped to which concept.
"""

import pandas as pd

from .config import ID_DTYPES, NDCP_XLSX


def load_ndcp(path=NDCP_XLSX) -> pd.DataFrame:
    """Return the raw NDCP county-year panel with identifiers as strings.

    Returns
    -------
    DataFrame
        One row per county x year, county FIPS kept as a 5-char zero-padded
        string.
    """
    raw = pd.read_excel(path, dtype=ID_DTYPES, engine="openpyxl")
    # TODO: select the columns you need, rename to snake_case, and reshape to
    # long format (county_fips, year, age_group, median_price) if that suits
    # your plotting. Assert the FIPS width before returning -- see
    # check_identifiers() below.
    return raw


def check_identifiers(df: pd.DataFrame, col: str, width: int) -> None:
    """Fail loudly if an identifier lost its leading zeros.

    Call this right after every read and every merge. A dropped zero does not
    raise -- it just silently produces unmatched rows later.
    """
    bad = df[col].astype(str).str.len().ne(width)
    if bad.any():
        raise ValueError(
            f"{col}: {bad.sum()} value(s) are not {width} characters wide. "
            f"Examples: {df.loc[bad, col].head().tolist()}"
        )


if __name__ == "__main__":
    df = load_ndcp()
    print(df.shape)
    print(df.head())

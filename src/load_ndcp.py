"""Load the NDCP county-level childcare price workbook.

Scope: read NDCP2022.xlsx off disk, keep the center-based median price columns,
and return a tidy county x year x age_group panel. No metro filtering and no
deflation -- those live in build_sample.py and deflate.py.

Column mapping, from Appendix C of the NDCP Technical Report (Sept 2024):

    MCInfant     Median price of Center-Based Care, infants    (0-23 months)
    MCToddler    Median price of Center-Based Care, toddlers   (24-35 months)
    MCPreschool  Median price of Center-Based Care, preschool  (36-54 months)

All three are aggregated weekly, full-time prices in nominal dollars, which is
what PS4 asks for. Deliberately NOT used:

    _75C*    75th-percentile center-based prices (assignment says median)
    MFCC*    family/home-based care (assignment says center-based)
    MC*to*   the narrow single-age-band columns these three aggregate

Each price column has a companion `*_flag` describing how the aggregate was
formed: 1 = one price matched the whole age range, 2 = modal price in the
range, 3 = highest of several modes. It is an aggregation indicator, not a
missingness flag; the flags are carried through so they can be inspected.

Note the workbook stores COUNTY_FIPS_CODE as a *number*, so Autauga County AL
arrives as 1001 rather than "01001". Zero-padding happens here, once, on read.
"""

import pandas as pd

from .config import FIPS_WIDTH, INTERIM, NDCP_XLSX, YEARS

# Parsing the 92 MB workbook takes ~95s. Cache the tidy result as parquet,
# which round-trips the string dtype on county_fips intact.
CACHE = INTERIM / "ndcp_center_median_tidy.parquet"

SHEET = "County_LevelNDCP_v8_update2008_"

# Age group -> (price column, flag column), as spelled in Appendix C. The
# workbook's header row uppercases the price columns but not the flags, so
# lookups here are case-insensitive.
PRICE_COLS = {
    "infant": ("MCInfant", "MCInfant_flag"),
    "toddler": ("MCToddler", "MCToddler_flag"),
    "preschool": ("MCPreschool", "MCPreschool_flag"),
}

ID_COLS = ["STATE_NAME", "STATE_ABBREVIATION", "COUNTY_NAME",
           "COUNTY_FIPS_CODE", "STUDYYEAR"]


def _resolve(columns, wanted):
    """Map a wanted column name to its actual spelling, ignoring case."""
    lookup = {c.lower(): c for c in columns}
    try:
        return lookup[wanted.lower()]
    except KeyError:
        raise KeyError(f"{wanted!r} not found in workbook. Got: {list(columns)[:10]}...")


def check_identifiers(df: pd.DataFrame, col: str, width: int) -> None:
    """Fail loudly if an identifier lost its leading zeros.

    Call this after every read and every merge. A dropped zero does not raise
    -- it just silently produces unmatched rows further downstream.
    """
    lengths = df[col].astype(str).str.len()
    bad = lengths.ne(width)
    if bad.any():
        raise ValueError(
            f"{col}: {bad.sum()} value(s) are not {width} characters wide. "
            f"Examples: {df.loc[bad, col].head().tolist()}"
        )


def load_ndcp_cached(refresh: bool = False) -> pd.DataFrame:
    """Tidy NDCP panel, reading the parquet cache when it is present."""
    if CACHE.exists() and not refresh:
        return pd.read_parquet(CACHE)
    df = load_ndcp()
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(CACHE, index=False)
    return df


def load_ndcp(path=NDCP_XLSX, years=YEARS, tidy: bool = True) -> pd.DataFrame:
    """Return center-based median prices as a county x year (x age group) panel.

    Parameters
    ----------
    path : Path
        The NDCP2022.xlsx workbook.
    years : iterable of int
        Study years to keep. Defaults to 2015-2022 per the assignment.
    tidy : bool
        True (default) returns long format, one row per county x year x age
        group, with columns ``median_price`` and ``agg_flag``. False returns
        wide format with one column per age group.

    Returns
    -------
    DataFrame
        ``county_fips`` is a 5-character zero-padded string; ``year`` is int.
    """
    raw = pd.read_excel(path, sheet_name=SHEET, engine="openpyxl")

    keep, rename = [], {}
    for c in ID_COLS:
        actual = _resolve(raw.columns, c)
        keep.append(actual)
        rename[actual] = c.lower()
    rename[_resolve(raw.columns, "COUNTY_FIPS_CODE")] = "county_fips"
    rename[_resolve(raw.columns, "STUDYYEAR")] = "year"

    for group, (price, flag) in PRICE_COLS.items():
        for col, suffix in ((price, ""), (flag, "_flag")):
            actual = _resolve(raw.columns, col)
            keep.append(actual)
            rename[actual] = f"{group}{suffix}"

    df = raw[keep].rename(columns=rename)

    # The workbook stores FIPS numerically; restore the zero padding before
    # anything tries to join on it.
    df["county_fips"] = (df["county_fips"].astype("Int64").astype(str)
                                          .str.zfill(FIPS_WIDTH))
    check_identifiers(df, "county_fips", FIPS_WIDTH)

    df["year"] = df["year"].astype(int)
    df = df[df["year"].isin(list(years))].copy()

    if not tidy:
        return df.reset_index(drop=True)

    id_vars = ["county_fips", "state_name", "state_abbreviation",
               "county_name", "year"]
    prices = df.melt(id_vars=id_vars, value_vars=list(PRICE_COLS),
                     var_name="age_group", value_name="median_price")
    flags = df.melt(id_vars=id_vars,
                    value_vars=[f"{g}_flag" for g in PRICE_COLS],
                    var_name="age_group", value_name="agg_flag")
    flags["age_group"] = flags["age_group"].str.removesuffix("_flag")

    out = prices.merge(flags, on=id_vars + ["age_group"], how="left")
    out["age_group"] = pd.Categorical(out["age_group"],
                                      categories=list(PRICE_COLS), ordered=True)
    out["median_price"] = pd.to_numeric(out["median_price"], errors="coerce")
    return out.sort_values(["year", "county_fips", "age_group"]).reset_index(drop=True)


if __name__ == "__main__":
    df = load_ndcp()
    print(df.shape)
    print(df.head(6).to_string(index=False))
    print(df.groupby("year", observed=True)["county_fips"].nunique())

"""Convert nominal dollars to constant 2022 dollars using CPI-U.

Series: CUUR0000SA0 (All Urban Consumers, U.S. city average, all items),
not seasonally adjusted, 1982-84 = 100. Source table saved verbatim at
data/raw/cpi/cpi_u_cuur0000sa0_monthly.txt so the numbers are auditable.

The BLS table publishes monthly index values. The **annual average** is the
simple mean of the 12 months -- that reproduces BLS's own published annual
averages exactly (2016 -> 240.007, 2022 -> 292.655), which `verify()` asserts.
A year with any month missing is skipped rather than averaged over fewer
months, so a partial year can never silently produce a wrong deflator.

Used by PS4 §3 (price trends), PS5 §5 (wages and rents), and the project.
Deflate every dollar series through `to_real` so the deliverables cannot end
up on different bases.
"""

import pandas as pd

from .config import BASE_YEAR, CPI_MONTHLY

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# BLS annual averages, for the assertion in verify(). Independent of the
# arithmetic below -- if a paste is mangled, the check fails loudly.
KNOWN_ANNUAL = {2016: 240.007, 2019: 255.657, 2022: 292.655}


def load_cpi_monthly(path=CPI_MONTHLY) -> pd.DataFrame:
    """Read the saved BLS monthly table. Returns year x month index values."""
    df = pd.read_csv(path, sep="\t", comment="#")
    df = df.rename(columns={df.columns[0]: "year"})
    df["year"] = df["year"].astype(int)
    for m in MONTHS:
        # "-(X)" marks a month BLS has not published; coerce to NaN.
        df[m] = pd.to_numeric(df[m], errors="coerce")
    return df.set_index("year")[MONTHS]


def load_cpi(path=CPI_MONTHLY) -> pd.Series:
    """Annual-average CPI-U indexed by year, complete years only."""
    monthly = load_cpi_monthly(path)
    complete = monthly.dropna(how="any")
    return complete.mean(axis=1).rename("cpi_u")


def deflators(base_year: int = BASE_YEAR, path=CPI_MONTHLY) -> pd.Series:
    """year -> multiplier converting nominal dollars to base-year dollars.

    The multiplier for year t is CPI[base] / CPI[t]. It equals exactly 1.0 in
    the base year, which is the cheap check that it is the right way up.
    """
    cpi = load_cpi(path)
    if base_year not in cpi.index:
        raise KeyError(f"CPI-U has no complete {base_year}; got {list(cpi.index)}")
    return (cpi.loc[base_year] / cpi).rename(f"to_{base_year}_dollars")


def to_real(df: pd.DataFrame, cols, year_col: str = "year",
            base_year: int = BASE_YEAR, path=CPI_MONTHLY) -> pd.DataFrame:
    """Add real-dollar counterparts of `cols`, suffixed `_real`.

    Nominal columns are kept alongside. PS4 §4 tests the voucher in NOMINAL
    terms (both voucher figures are given nominal), while §3 plots real
    trends -- both are needed in the same frame.

    Rows whose year has no complete CPI year get NaN in the `_real` column
    rather than being dropped, so the caller decides what to do about them.
    """
    cols = [cols] if isinstance(cols, str) else list(cols)
    mult = deflators(base_year, path)
    out = df.copy()
    factor = out[year_col].map(mult)
    for c in cols:
        out[f"{c}_real"] = out[c] * factor
    out[f"cpi_factor_{base_year}"] = factor
    return out


def verify(path=CPI_MONTHLY) -> pd.DataFrame:
    """Cross-check computed annual averages against published BLS values."""
    cpi = load_cpi(path)
    for year, published in KNOWN_ANNUAL.items():
        if year in cpi.index:
            got = round(cpi.loc[year], 3)
            assert got == published, f"{year}: computed {got}, BLS says {published}"
    d = deflators(path=path)
    assert d.loc[BASE_YEAR] == 1.0, "base-year multiplier must be exactly 1.0"
    return pd.DataFrame({"cpi_u_annual": cpi.round(3),
                         f"to_{BASE_YEAR}_dollars": d.round(5)})


if __name__ == "__main__":
    print(verify().to_string())

"""Define the metro county sample shared by PS4, PS5, and the final project.

This is the single place the county set is decided. PS4 §1 requires that all
three deliverables use the same one, so nothing downstream should re-filter.

The rule, from the assignment's "Geography & crosswalks" section:

  - join counties to OEWS areas via data/crosswalks/county_oews_crosswalk.csv
    on [year, county] -- the crosswalk is YEAR-SPECIFIC, so a county can
    change area across years
  - keep counties whose oews_area begins "00" (metro); drop the rest
  - carry area_title through, for labelling metros later

Requires data/crosswalks/county_oews_crosswalk.csv (course-provided, not
downloadable). Run `python -m src.build_sample` once it is in place.
"""

import pandas as pd

from .config import (FIPS_WIDTH, METRO_AREA_PREFIX, OEWS_AREA_WIDTH,
                     OEWS_CROSSWALK, PROCESSED, YEARS)
from .load_ndcp import check_identifiers, load_ndcp_cached

OUT = PROCESSED / "ps4_metro_prices_2015_2022.parquet"

# The crosswalk's county identifier column -- spelling not yet confirmed
# against the file, so accept the plausible variants and fail loudly if none
# of them is present.
_COUNTY_ALIASES = ["county_fips", "fips", "county_fips_code", "countyfips",
                   "county_code", "fips_code", "geoid"]
_YEAR_ALIASES = ["year", "studyyear", "yr"]


def _pick(columns, aliases, label):
    lookup = {c.lower().strip(): c for c in columns}
    for a in aliases:
        if a in lookup:
            return lookup[a]
    raise KeyError(
        f"Could not find the {label} column in the crosswalk. "
        f"Tried {aliases}; file has {list(columns)}"
    )


def load_crosswalk(path=OEWS_CROSSWALK) -> pd.DataFrame:
    """Read the course-provided county x year -> OEWS area crosswalk.

    Both identifiers are read as strings and re-padded: county FIPS to 5 chars,
    oews_area to 7. If the file was ever opened and re-saved in Excel the
    leading zeros may already be gone, so pad defensively rather than trusting
    the file.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"{path} is missing. It is provided by the course (not a public "
            "download) -- copy it from the course site into data/crosswalks/."
        )

    xw = pd.read_csv(path, dtype=str)
    county_col = _pick(xw.columns, _COUNTY_ALIASES, "county")
    year_col = _pick(xw.columns, _YEAR_ALIASES, "year")
    area_col = _pick(xw.columns, ["oews_area"], "OEWS area")
    title_col = _pick(xw.columns, ["area_title"], "area title")

    xw = xw.rename(columns={county_col: "county_fips", year_col: "year",
                            area_col: "oews_area", title_col: "area_title"})
    xw = xw[["county_fips", "year", "oews_area", "area_title"]]

    xw["county_fips"] = xw["county_fips"].str.strip().str.zfill(FIPS_WIDTH)
    xw["oews_area"] = xw["oews_area"].str.strip().str.zfill(OEWS_AREA_WIDTH)
    xw["year"] = xw["year"].astype(int)

    check_identifiers(xw, "county_fips", FIPS_WIDTH)
    check_identifiers(xw, "oews_area", OEWS_AREA_WIDTH)
    return xw


def metro_counties(crosswalk: pd.DataFrame | None = None) -> pd.DataFrame:
    """County x year rows that define the metro analysis sample.

    Keeps OEWS area codes beginning "00" and restricts to YEARS.
    """
    xw = load_crosswalk() if crosswalk is None else crosswalk
    metro = xw[xw["oews_area"].str.startswith(METRO_AREA_PREFIX)]
    metro = metro[metro["year"].isin(list(YEARS))]
    return metro.reset_index(drop=True)


def build(write: bool = True) -> pd.DataFrame:
    """Restrict NDCP center-based median prices to the metro sample.

    Inner join on [county_fips, year], so the result is exactly the counties
    that are in an OEWS metro area AND present in NDCP.

    Persisted as parquet, not CSV: parquet preserves the string dtype on
    county_fips and oews_area, so a round-trip cannot reintroduce the
    leading-zero bug.
    """
    prices = load_ndcp_cached()
    metro = metro_counties()

    n_price_counties = prices["county_fips"].nunique()
    n_metro_counties = metro["county_fips"].nunique()

    df = prices.merge(metro, on=["county_fips", "year"], how="inner")
    check_identifiers(df, "county_fips", FIPS_WIDTH)
    check_identifiers(df, "oews_area", OEWS_AREA_WIDTH)

    print(f"NDCP counties (any year):        {n_price_counties:>6,}")
    print(f"metro counties in crosswalk:     {n_metro_counties:>6,}")
    print(f"metro counties in both:          {df['county_fips'].nunique():>6,}")
    print(f"rows (county x year x agegroup): {len(df):>6,}")
    print(f"metro areas represented:         {df['oews_area'].nunique():>6,}")
    print("\nmissing median_price by age group:")
    print(df.groupby("age_group", observed=True)["median_price"]
            .apply(lambda s: f"{s.isna().mean():.2%}"))

    if write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(OUT, index=False)
        print(f"\nwrote {OUT.relative_to(OUT.parents[2])}")
    return df


if __name__ == "__main__":
    build()

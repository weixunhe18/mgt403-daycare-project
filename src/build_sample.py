"""Define the metro county sample shared by PS4, PS5, and the final project.

This is the single place the county set is decided. PS4 §1 requires that all
three deliverables use the same one, so nothing downstream should re-filter.

The rule, from the assignment's "Geography & crosswalks" section:

  - join counties to OEWS areas via data/crosswalks/county_oews_crosswalk.csv
    on [year, oews_area] -- the crosswalk is YEAR-SPECIFIC, so a county can
    change area across years
  - keep counties whose oews_area begins "00" (metro); drop the rest
  - carry area_title through, for labelling metros later
"""

import pandas as pd

from .config import ID_DTYPES, METRO_AREA_PREFIX, OEWS_CROSSWALK, YEARS
from .load_ndcp import check_identifiers


def load_crosswalk(path=OEWS_CROSSWALK) -> pd.DataFrame:
    """Read the course-provided county x year -> OEWS area crosswalk."""
    return pd.read_csv(path, dtype=ID_DTYPES)


def metro_counties(crosswalk: pd.DataFrame) -> pd.DataFrame:
    """Restrict the crosswalk to metropolitan areas.

    Returns the county x year rows that define the analysis sample, plus
    area_title for labelling.
    """
    # TODO: filter on oews_area starting with METRO_AREA_PREFIX, restrict to
    # YEARS, and return the columns you need downstream.
    raise NotImplementedError


def build(write: bool = True) -> pd.DataFrame:
    """Assemble and optionally persist the metro sample.

    Persist to parquet, not CSV: parquet preserves the string dtype on
    county_fips and oews_area, so a round-trip cannot reintroduce the
    leading-zero bug.
    """
    raise NotImplementedError


if __name__ == "__main__":
    build()

"""PS4 figures: the distribution of 2022 center-based median prices.

Small multiples rather than overlaid histograms — three distributions on one
axis would occlude each other, and the point of the figure is the shift ACROSS
age groups, which stacked panels on a shared x-axis show directly.

    python -m src.ps4_figures
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .config import BASE_YEAR, FIGURES, PROCESSED, TABLES, ensure_dirs

SAMPLE = PROCESSED / "ps4_metro_prices_2015_2022.parquet"

# Validated categorical slots 1-3 (all-pairs, light surface). Age group is the
# identity here, so hues are assigned in fixed order and never cycled.
SERIES = {"infant": "#2a78d6", "toddler": "#eb6834", "preschool": "#1baf7a"}
LABEL = {"infant": "Infant (0–23 months)",
         "toddler": "Toddler (24–35 months)",
         "preschool": "Preschool (36–54 months)"}

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_MUTED = "#52514e"
GRID = "#e4e3df"

BIN_WIDTH = 10   # dollars/week


def load_2022() -> pd.DataFrame:
    df = pd.read_parquet(SAMPLE)
    return df[(df["year"] == BASE_YEAR) & df["median_price"].notna()].copy()


def descriptives(df: pd.DataFrame) -> pd.DataFrame:
    """mean / SD / N per age group, for annotating the panels."""
    out = (df.groupby("age_group", observed=True)["median_price"]
             .agg(n="count", mean="mean", sd=lambda s: s.std(ddof=1),
                  median="median", p_min="min", p_max="max"))
    return out.round(2)


def histograms(df: pd.DataFrame, stats: pd.DataFrame, path=None):
    """Stacked small multiples on a shared x-axis, one panel per age group."""
    # Common bin edges so the panels are directly comparable.
    lo = np.floor(df["median_price"].min() / BIN_WIDTH) * BIN_WIDTH
    hi = np.ceil(df["median_price"].max() / BIN_WIDTH) * BIN_WIDTH
    bins = np.arange(lo, hi + BIN_WIDTH, BIN_WIDTH)

    fig, axes = plt.subplots(3, 1, figsize=(9, 8.2), sharex=True,
                             facecolor=SURFACE)
    fig.subplots_adjust(hspace=0.38)

    for ax, group in zip(axes, SERIES):
        s = df.loc[df["age_group"] == group, "median_price"]
        row = stats.loc[group]

        ax.set_facecolor(SURFACE)
        ax.hist(s, bins=bins, color=SERIES[group], edgecolor=SURFACE,
                linewidth=0.6)

        # Mean marker: a thin rule beats a second color here.
        ax.axvline(row["mean"], color=INK, linewidth=1.4, linestyle=(0, (4, 2)),
                   zorder=3)
        ax.annotate(f"mean \\${row['mean']:,.0f}",
                    xy=(row["mean"], ax.get_ylim()[1]),
                    xytext=(6, -12), textcoords="offset points",
                    color=INK, fontsize=9, va="top")

        ax.set_title(LABEL[group], loc="left", fontsize=11.5, color=INK,
                     pad=8, fontweight="medium")
        # Escape the dollar signs: an unescaped pair makes matplotlib parse the
        # span between them as mathtext.
        ax.annotate(f"N = {row['n']:,.0f}   SD = \\${row['sd']:,.0f}"
                    f"   median = \\${row['median']:,.0f}",
                    xy=(1, 1), xycoords="axes fraction", xytext=(0, 8),
                    textcoords="offset points", ha="right", fontsize=9,
                    color=INK_MUTED)

        ax.grid(axis="y", color=GRID, linewidth=0.7)
        ax.set_axisbelow(True)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_color(GRID)
        ax.tick_params(colors=INK_MUTED, labelsize=9, length=0)
        ax.set_ylabel("Counties", fontsize=9.5, color=INK_MUTED)

    axes[-1].set_xlabel("Median weekly price, center-based care (2022 nominal $)",
                        fontsize=10, color=INK_MUTED, labelpad=8)

    fig.suptitle("Childcare prices rise steeply with how young the child is",
                 x=0.055, y=0.985, ha="left", fontsize=14, color=INK,
                 fontweight="semibold")
    fig.text(0.055, 0.945,
             "Weekly median price per county, center-based care, 2022. Metro "
             f"analysis sample; {len(df['county_fips'].unique()):,} of 1,236 "
             "counties report a price. Source: DOL NDCP.",
             ha="left", fontsize=9.5, color=INK_MUTED)

    path = path or FIGURES / "ps4_hist_median_price_2022.png"
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)
    return path


def real_panel() -> pd.DataFrame:
    """Metro sample with prices deflated to constant BASE_YEAR dollars."""
    from .deflate import to_real
    df = pd.read_parquet(SAMPLE)
    df = to_real(df, "median_price")
    return df[df["median_price_real"].notna()].copy()


def balanced_counties(df: pd.DataFrame) -> set:
    """Counties reporting a price in every year the CPI covers.

    The share of counties reporting swings from 14% to 26% missing across
    years, so a mean over 'whoever reported' mixes a real price trend with a
    changing roster of counties. This isolates the roster that never changes.
    """
    pre = df[df["age_group"] == "preschool"]
    n_years = pre["year"].nunique()
    per_county = pre.groupby("county_fips")["year"].nunique()
    return set(per_county[per_county == n_years].index)


def trends(df: pd.DataFrame, path=None):
    """Real price trend per age group: full sample vs balanced panel."""
    bal = balanced_counties(df)

    def series(frame):
        return frame.pivot_table(index="year", columns="age_group",
                                 values="median_price_real", aggfunc="mean",
                                 observed=True)

    all_s = series(df)
    bal_s = series(df[df["county_fips"].isin(bal)])
    years = all_s.index.to_list()

    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.9), sharey=True,
                             facecolor=SURFACE)
    fig.subplots_adjust(wspace=0.09)

    C_ALL, C_BAL = "#2a78d6", "#eb6834"

    for i, (ax, group) in enumerate(zip(axes, SERIES)):
        ax.set_facecolor(SURFACE)
        ax.plot(years, all_s[group], color=C_ALL, linewidth=2,
                marker="o", markersize=5, label="All reporting counties")
        ax.plot(years, bal_s[group], color=C_BAL, linewidth=2,
                marker="o", markersize=5, label=f"Balanced panel ({len(bal)})")

        ax.set_title(LABEL[group], loc="left", fontsize=11.5, color=INK, pad=8)
        ax.grid(axis="y", color=GRID, linewidth=0.7)
        ax.set_axisbelow(True)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_color(GRID)
        ax.tick_params(colors=INK_MUTED, labelsize=9, length=0)
        ax.set_xticks(years)
        ax.set_xticklabels([str(y) for y in years], rotation=45, ha="right")
        if i == 0:
            ax.set_ylabel(f"Mean of county median prices\n"
                          f"(constant {BASE_YEAR} $/week)",
                          fontsize=9.5, color=INK_MUTED)

    axes[0].legend(frameon=False, fontsize=9.5, loc="lower left",
                   labelcolor=INK_MUTED)

    fig.suptitle("Real childcare prices drifted up through 2020, then fell as "
                 "inflation outran them",
                 x=0.043, y=1.03, ha="left", fontsize=14, color=INK,
                 fontweight="semibold")
    fig.text(0.043, 0.965,
             f"Deflated with CPI-U (CUUR0000SA0, annual averages), constant "
             f"{BASE_YEAR} dollars. The 2021 dip in the full sample is largely "
             "composition — that year has the fewest reporting counties.",
             ha="left", fontsize=9.5, color=INK_MUTED)

    path = path or FIGURES / "ps4_trend_real_by_agegroup.png"
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)
    return path, all_s, bal_s


if __name__ == "__main__":
    ensure_dirs()
    df = load_2022()
    stats = descriptives(df)
    print(stats.to_string())
    stats.to_csv(TABLES / "ps4_descriptives_2022.csv")
    print("\nfigure:", histograms(df, stats))

    real = real_panel()
    path, all_s, bal_s = trends(real)
    print("\n== mean county median price, constant 2022 $ ==")
    print("all reporting counties:\n", all_s.round(1).to_string())
    print("\nbalanced panel:\n", bal_s.round(1).to_string())
    all_s.round(2).to_csv(TABLES / "ps4_trend_real_all.csv")
    bal_s.round(2).to_csv(TABLES / "ps4_trend_real_balanced.csv")
    print("\nfigure:", path)

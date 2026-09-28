# MGT-403 Data Project — Where Should We Open Our Next Daycare?

Price/cost/demand dataset built from three public sources, covering Problem
Set 4, Problem Set 5, and the final market-selection project.

One repo for all three deliverables, deliberately: PS4 §1 requires a
consistent county set, and the CPI-U deflator and OEWS crosswalk are reused
throughout. Shared logic lives in `src/` and is written once.

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```

Then populate `data/raw/` — it's gitignored, so a fresh clone starts empty.
Every URL and the expected filename is in [data/raw/SOURCES.md](data/raw/SOURCES.md).

## Re-running the analysis

```bash
python -m src.build_sample     # metro county sample -> data/processed/
jupyter lab notebooks/ps4_prices.ipynb
```

## Layout

| Path | What's there |
|---|---|
| `data/raw/` | Downloads, never edited. Gitignored; rebuild from `SOURCES.md`. |
| `data/crosswalks/` | Course-provided `county_oews_crosswalk.csv`. Committed. |
| `data/interim/` | Disposable intermediates. |
| `data/processed/` | Built analysis datasets (parquet, to preserve string IDs). |
| `src/` | Importable logic — config, loaders, sample definition, deflation. |
| `notebooks/` | Thin analysis + narrative. Imports `src/`, holds no logic. |
| `output/figures`, `output/tables` | Generated artifacts. Regenerable. |
| `deliverables/` | Rendered write-ups and slides, per deliverable. |
| `DECISIONS.md` | Append-only log of data-handling calls → project appendix. |

### Why logic sits in `src/` and not in the notebooks

Jupyter `.ipynb` files are JSON and merge catastrophically — two people editing
one notebook produces a conflict git can't resolve. Keeping the real code in
`.py` modules means teammates can work in parallel on the same analysis.

## Working agreement

- Branch per person (`weixun/ps4-descriptives`), PR into `main`.
- Log every data-handling judgment call in `DECISIONS.md` as you make it.
- Fill in the `SOURCES.md` row the moment you download a file.
- Never commit an API key. Census keys go in a local `.env`.

## Who's doing what

| Section | Owner |
|---|---|
| PS4 §2 descriptives + histograms | |
| PS4 §3 deflation + trends | |
| PS4 §4 voucher hypothesis test | |

## Traps the assignment calls out

1. **Leading zeros.** County FIPS is 5 chars, OEWS area is 7 — both zero-padded
   strings. Read as int and the join silently under-matches.
2. **Metro filter.** Keep `oews_area` starting `00`; drop the rest. Applied
   once, in `src/build_sample.py`.
3. **NDCP column choice.** Center-based *and* median (not 75th percentile),
   correct age group. Needs Appendix C of the Technical Report.
4. **Units in PS4 §4.** NDCP prices are weekly; the CCDF voucher is monthly.
   4.33 weeks/month, and state the conversion direction in the write-up.
5. **The crosswalk is year-specific.** Join on `[year, oews_area]`, not area
   alone.

## Submission

Per the assignment, either this repo (or a zip of it) plus slides. `README.md`
+ `DECISIONS.md` + `SOURCES.md` together are what make the work re-runnable by
someone who has only the repo.

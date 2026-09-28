# Data handling decisions

Append-only log of judgment calls. **Write the entry when you make the call**,
not at the end — this file becomes the appendix the final project requires
("submit an appendix document that details any important data handling
decisions you made", p. 6), and it's what lets a grader follow your reasoning.

Append-only also means teammates don't fight over the same lines in a merge.

Format: one dated entry per decision.

```
## YYYY-MM-DD — short title  (author)
**Decision:** what you did.
**Why:** the reasoning, and what the alternatives were.
**Affects:** PS4 §n / PS5 §n / project.
```

---

## 2026-09-28 — Metro sample defined once, in `src/build_sample.py`  (Weixun)
**Decision:** The metro county set (OEWS area code beginning `00`) is computed
in one place and reused by PS4, PS5, and the project; no notebook re-filters.
**Why:** PS4 §1 requires a consistent county set across all three deliverables.
Filtering in each notebook invites drift that wouldn't surface as an error.
**Affects:** all.

## 2026-09-28 — Identifiers read as strings, width-asserted after every merge  (Weixun)
**Decision:** `county_fips` (5 chars) and `oews_area` (7 chars) are read with
explicit `str` dtypes; `check_identifiers()` runs after each read and join.
**Why:** The assignment warns twice about dropped leading zeros. The failure is
silent — the join just returns fewer matches — so it needs an active check.
**Affects:** all.

## 2026-09-28 — NDCP price columns: `MCInfant` / `MCToddler` / `MCPreschool`  (Weixun)
**Decision:** PS4 uses these three columns only. They are the aggregated
weekly, full-time **median** prices for **center-based** care, for infants
(0–23 mo), toddlers (24–35 mo), and preschool (36–54 mo).
**Why:** Appendix C of the Technical Report (p.51–66). The assignment
specifies center-based and median, which rules out `_75C*` (75th percentile)
and `MFCC*` (family/home-based). The narrow single-age-band columns
(`MCBto5`, `MC6to11`, …) are what these three aggregate, so using both would
double-count.
**Affects:** PS4 §2–§4, project.

## 2026-09-28 — County FIPS zero-padded on read  (Weixun)
**Decision:** `COUNTY_FIPS_CODE` is cast to a 5-char zero-padded string inside
`load_ndcp()`.
**Why:** Appendix C documents the field as "Numeric", and the workbook does
store it that way — Autauga County AL reads as `1001`, not `01001`. Every
Alabama/Alaska/etc. county would fail the crosswalk join silently.
**Affects:** all.

## 2026-09-28 — `*_flag` columns carried through, not used to filter  (Weixun)
**Decision:** Kept `agg_flag` alongside each price; no rows dropped on it.
**Why:** Per Appendix C the flag records how the age-range aggregate was
formed (1 = a single price matched the whole range, 2 = modal price, 3 =
highest of several modes). It describes aggregation method, not data quality
or imputation, so it isn't grounds for exclusion — but it's worth being able
to check sensitivity later.
**Affects:** PS4 §2–§4.

## 2026-09-28 — Tidy NDCP panel cached to parquet  (Weixun)
**Decision:** `load_ndcp_cached()` writes
`data/interim/ndcp_center_median_tidy.parquet`; delete it to force a re-parse.
**Why:** Parsing the 92 MB workbook takes ~97s vs ~1.8s from cache. Parquet
(not CSV) because it preserves the string dtype on `county_fips`, so a
round-trip can't reintroduce the leading-zero bug.
**Affects:** all.

## 2026-09-28 — Metro sample built: 1,236 counties, 390 metro areas  (Weixun)
**Decision:** The PS4/PS5/project county set is the inner join of NDCP prices
and the metro rows of `county_oews_crosswalk.csv`, on `[county_fips, year]`.
**Why:** 1,238 metro counties in the crosswalk; 1,236 match NDCP. Written to
`data/processed/ps4_metro_prices_2015_2022.parquet` (29,619 county × year ×
age-group rows).
**Affects:** all.

## 2026-09-28 — Two crosswalk counties have no NDCP match (kept as dropped)  (Weixun)
**Decision:** `12025` (Miami–Fort Lauderdale–West Palm Beach, FL) and `51515`
(Lynchburg, VA) appear in the crosswalk but not in NDCP; the inner join drops
them. Not patched.
**Why:** Both are retired FIPS codes — 12025 is the old Dade County (now
Miami-Dade, 12086) and 51515 is Bedford city VA, which reverted to town status
in 2013 and folded into Bedford County (51019). NDCP uses current codes.
Remapping them would double-count if the successor county is already present.
**Affects:** all. Worth a sentence in the project appendix.

## 2026-09-28 — NDCP price missingness is real, not a merge failure  (Weixun)
**Decision:** ~14–26% of metro county-years have no center-based median price.
Rows kept with NaN; descriptives report N per cell rather than silently
dropping.
**Why:** Missingness by year (preschool): 2015 18.7%, 2016 16.9%, 2017–2020
~13.9%, **2021 25.7%**, 2022 18.0%. It is evenly spread across age groups
(16.83–16.89% overall), which is what a genuine survey gap looks like — a
broken join would hit all three identically at 100% or skew by state. The
assignment's ~1% missingness warning applies to BLS wage cells in PS5, not to
NDCP prices.
**Affects:** PS4 §2–§4. 2021's spike is worth a note when discussing trends.

## 2026-09-28 — External validation against Appendix H  (Weixun)
**Decision:** Treat the 2022 preschool extract as correct.
**Why:** Our metro 2022 `MCPreschool` max is 496.30, exactly the top of
quintile 5 in Appendix H Exhibit A; the min (86.19) falls inside quintile 1
(83.23–113.80). Independent confirmation that the right column, year, and
provider type were selected.
**Affects:** PS4 §2.

<!-- Add entries below. Things that will need one:
     - which NDCP columns map to center-based / median / preschool
     - how you handle counties missing prices in some years
     - CPI-U vintage and the exact base you deflated to
     - treatment of BLS-suppressed wage cells (~1% expected, PS5 §3)
-->

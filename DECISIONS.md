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

<!-- Add entries below. Things that will need one:
     - which NDCP columns map to center-based / median / preschool
     - how you handle counties missing prices in some years
     - CPI-U vintage and the exact base you deflated to
     - treatment of BLS-suppressed wage cells (~1% expected, PS5 §3)
-->

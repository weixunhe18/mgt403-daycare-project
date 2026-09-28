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

<!-- Add entries below. Things that will need one:
     - which NDCP columns map to center-based / median / preschool
     - how you handle counties missing prices in some years
     - CPI-U vintage and the exact base you deflated to
     - treatment of BLS-suppressed wage cells (~1% expected, PS5 §3)
-->

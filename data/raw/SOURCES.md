# Data sources

`data/raw/` is gitignored — the files are large and all of them are freely
re-downloadable. This file is the substitute: it records exactly what was
pulled, from where, and when, so anyone can rebuild `data/raw/` from scratch.

**Fill in a row the moment you download something.** Reconstructing this later
is guesswork, and the project appendix (final project, p. 6) has to document
data handling decisions.

---

## 1. NDCP — childcare prices (PS4, project)

| Field | Value |
|---|---|
| Source | U.S. Dept. of Labor, National Database of Childcare Prices |
| Page | https://www.dol.gov/agencies/wb/topics/featured-childcare |
| File | `ndcp/NDCP2022.xlsx` (county-level workbook, series through 2022) |
| Downloaded | _YYYY-MM-DD_ |
| By | _name_ |
| Size / rows | _fill in_ |
| Notes | Also save the Technical Report (Sept 2024) here — Appendix C is the county-level data dictionary. |

## 2. CPI-U — inflation adjustment (PS4 §3, PS5 §5, project)

| Field | Value |
|---|---|
| Source | BLS series **CUUR0000SA0**, annual averages |
| Page | https://www.bls.gov/cpi |
| File | `cpi/cpi_u_cuur0000sa0_annual.csv` |
| Downloaded | _YYYY-MM-DD_ |
| By | _name_ |
| Notes | Annual averages, not-seasonally-adjusted. Record which years you pulled. |

## 3. OEWS — childcare worker wages (PS5)

| Field | Value |
|---|---|
| Source | BLS Occupational Employment and Wage Statistics |
| Pattern | `https://www.bls.gov/oes/special-requests/oesmYYma.zip` (YY = 15…22) |
| Files | `oews/oesm15ma.zip` … `oesm22ma.zip` |
| Downloaded | _YYYY-MM-DD_ |
| By | _name_ |
| Notes | SOC **39-9011** Childcare Workers, mean annual wage, metro/nonmetro area level. |

## 4. ACS 5-year — demand and rent (PS5)

| Field | Value |
|---|---|
| Source | Census API, `acs/acs5`, county level |
| Endpoint | `https://api.census.gov/data/{year}/acs/acs5?get=...&for=county:*&in=state:*` |
| Files | `acs/acs5_counties_{year}.csv` |
| Pulled | _YYYY-MM-DD_ |
| By | _name_ |
| Notes | API key is personal — keep it in a local `.env`, never commit it. Log the exact variable list you requested. |

## 5. OEWS crosswalk — provided by the course

Lives in `data/crosswalks/county_oews_crosswalk.csv` and **is** committed: it
is small and not re-downloadable from a public URL. Maps county × year →
`oews_area` (7 chars) + `area_title`.

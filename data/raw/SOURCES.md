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
| File | `ndcp/NDCP2022.xlsx` — https://www.dol.gov/sites/dolgov/files/WB/NDCP2022.xlsx |
| Downloaded | 2026-09-28 |
| By | Weixun He |
| Size / rows | 91,691,849 bytes; sheet `County_LevelNDCP_v8_update2008_`, 48,309 rows × 370 cols, study years 2008–2022 |
| Docs | `ndcp/National-Database-of-Childcare-Prices-Technical-Report.pdf` (Sept 2024, 154pp; **Appendix C p.51–66** is the county-level data dictionary) and `ndcp/NationalDatabaseofChildcarePricesTechnicalGuide-2022.pdf` |
| Notes | dol.gov sits behind Akamai and returns 403 to a bare `curl`; full browser headers (UA + `Sec-Fetch-*` + `Referer`) get through. |

## 2. CPI-U — inflation adjustment (PS4 §3, PS5 §5, project)

| Field | Value |
|---|---|
| Source | BLS series **CUUR0000SA0**, All items, U.S. city average, not seasonally adjusted, 1982-84 = 100 |
| Page | https://www.bls.gov/cpi |
| File | `cpi/cpi_u_cuur0000sa0_monthly.txt` |
| Retrieved | 2026-09-29, pasted from the BLS series table |
| By | Weixun He |
| Coverage | **2016–2025 monthly.** 2015 is absent — still needed, the assignment range is 2015–2022 |
| Notes | BLS publishes monthly values; the annual average is the mean of the 12 months. `src/deflate.py` computes it and asserts 2016/2019/2022 against published annual averages (240.007 / 255.657 / 292.655). Years with any month missing are skipped, so 2025 (`-(X)` for October) is excluded automatically. |

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

| Field | Value |
|---|---|
| Received | 2026-09-28, from the course site |
| Size | 1,496,816 bytes; 25,859 data rows |
| Columns | `county_fips, state_abbr, year, oews_area, area_title` |
| Notes | Leading zeros intact as distributed (`01001`, `0033860`). Don't open and re-save it in Excel — that strips them. 1,238 counties carry a metro (`00…`) area code. |

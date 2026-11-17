# Provenance of the implied emission factors

An **implied** emission factor is worked back from reported inventory totals (kt CO2 divided by area). It is not a measured or default IPCC value. This page records, for each implied factor in the database
(`src/landcover_lca/database/landcover_lca_database.db`, table `emission_factors_land_use`), where it came from, how it was derived, and how to refresh it. The database also holds a `source` row and a `units` row under each factor; the `units` labels are legacy and not reliable (the unit is stated here).

**Source data for the two soil factors:** EPA CRT Table 4.C (Grassland), **2026 submission**, one workbook per year 1990-2024 (`IRL-CRT-2026-V1.0-<year>.xlsx`). The mineral-soil rows are extracted by `tools/extract_crt_table4c.py` into `tests/data/inventory/crt2026_4c_mineral_soils.csv` (and `crt2026_forest_conversions_mineral_soils.csv` for the cross-check below). The method is laid out step by step in the next section. CRT sign convention: + = gain of carbon, - = loss. The extract flips it to the package convention (+ emission, - removal): kg CO2/ha = -(t C/ha) x 1000 x 44/12. The 4.C.1 rows reproduce the NID 2026 key category table (+107.27 kt CO2 in 1990, -1,549.47 kt CO2 in 2024).

## Method, step by step (both soil factors)

1. **Get the data.** The EPA's 2026 CRT submission is one Excel workbook per inventory year, `IRL-CRT-2026-V1.0-<year>.xlsx`, 1990-2024. In this repository they are in `artifacts/data/national-inventory-2026/IRL-CRT-2026-V1.0/` (the folder is not committed to git; the zip is the EPA download).
2. **Find the rows.** In each workbook open sheet `Table4.C` (Grassland, "Sectoral background data"). The rows are found by their label, not by row number: `4.C.1. Grassland remaining grassland` and `4.C.2. Land converted to grassland` (in Ireland 4.C.2 is forest land only, row `4.C.2.a`).
3. **Read four cells from each row** (Excel columns): **D** total area (kha); **E** area of mineral soil (kha; for 4.C.2 the mineral area is the total area D, because the row has no organic soil); **K** implied net carbon stock change in mineral soils (t C per ha per year); **Q** net carbon stock change in mineral soils (kt C). These are the headings "Net carbon stock change in soils per area, Mineral soils" and "Carbon stock changes, Net carbon stock change in soils, Mineral soils".
4. **Change the sign.** The CRT reports + for a gain of carbon and - for a loss. The package reports + for an emission and - for a removal, so the sign is flipped. Convert carbon to CO2 with 44/12: `kt CO2 = -kt C x 44/12` and `kg CO2 per ha = -(t C per ha) x 1000 x 44/12`.
5. **Pool five years.** Take the latest five years, 2020-2024. Add the kt CO2 of the five years, add the mineral areas of the five years, and divide: `factor (kg CO2/ha/yr) = sum of kt CO2 / sum of area (kha) x 1000`. This weights each year by its area; it is not the average of the five yearly factors (for the grassland factor the two differ by less than 0.01 kg CO2/ha; for the forest factor they are identical because the CRT applies one constant rate).
6. **Store the result** in the database (value in the `ireland` row, source text in the `source` row; the table has three rows) and record it on this page.
7. **Check it** with `tests/implied_factor_test.py`, which repeats steps 3 to 5 from the stored extract and compares with the database. Steps 2 to 4 are scripted in `tools/extract_crt_table4c.py`; step 5 in `tools/derive_implied_grassland_factor.py`.

**Why 2020-2024 and not one year.** The EPA recalculates the full time series each submission, so a single year is not stable. A scenario baseline is usually 2020 but not always, so the factor should describe recent conditions. Five years is long enough to damp year-to-year change and short enough to stay recent.

## ef_co2_implied_grassland_remaining_SOC_per_ha

| | |
|---|---|
| Value | **-392.73** kg CO2 per hectare of mineral grassland per year (-392.7346...; negative = removal) |
| Used by | `Grassland.mineral_co2_in_grassland` (`land_classes/grassland.py`): mineral grassland area x this factor, every year and scenario. The only SOC term in the goblin_lite national case |
| Inventory category | CRT 4.C.1 Grassland remaining grassland, mineral soils (NID 2026 s.6.5; Tier 1) |
| Source data | CRT Table 4.C, **2026 submission**, years 2020-2024 |
| Derivation | **sum of kt CO2 / sum of mineral area (kha) x 1000** over 2020-2024: -7,593.19 kt / 19,334.16 kha = -392.73 kg CO2/ha/yr |
| Yearly values | 2020 -386.62, 2021 -391.90, 2022 -392.14, 2023 -392.23, 2024 -400.80 |
| Scripts | `tools/extract_crt_table4c.py` (extract), `tools/derive_implied_grassland_factor.py` (derive) |
| Test | `tests/implied_factor_test.py` recomputes the value from the stored extract and checks the database |
| Derived | November 2026 |

**Worked numbers, 4.C.1 (grassland remaining grassland, mineral soils).**

| Year | Mineral area (kha) | Soil C change, CRT sign (kt C) | kt CO2 (package sign) | kg CO2/ha/yr |
|---|---|---|---|---|
| 2020 | 3,869.0539 | 407.9569 | -1,495.8419 | -386.62 |
| 2021 | 3,867.6271 | 413.3797 | -1,515.7254 | -391.90 |
| 2022 | 3,866.3846 | 413.4973 | -1,516.1567 | -392.14 |
| 2023 | 3,865.1199 | 413.4557 | -1,516.0043 | -392.23 |
| 2024 | 3,865.9760 | 422.5816 | -1,549.4660 | -400.80 |
| **Sum** | **19,334.1615** | **2,070.8712** | **-7,593.1943** | **-392.7346** |

The last cell is the factor: -7,593.19 kt CO2 / 19,334.16 kha x 1000.

**Why a five-year average of the latest submission.** The EPA recalculates the whole time series every submission, so a single year is not stable. A baseline year is usually 2020 but not always, so the factor should represent recent conditions, not one year. Pooling kt and area weights each year by its area.

**Assumptions to be aware of.**
- The constant is applied to every year of every scenario, including years after the inventory. The sink continuing unchanged is a modelling assumption, not an inventory fact. The inventory series is not constant: it runs from +26.6 kg/ha (1990) to about -400 (2018-2024), driven mainly by the shift from improved grassland to rough grazing (NID s.6.5.2.4).
- The NID publishes only totals for this category, not a per-hectare factor or a mineral-area table, so a derived value is needed.
- The package's mineral grassland area (3,595.7 kha in the goblin_lite 2020 baseline) is 7.1% below the inventory's 2020 mineral area (3,869.1 kha). The factor is not the cause; the area comes from landcover_assignment.

**History.** Original value -371.985 (`NIR, 2024`), derived by the database author from the CRF and added between June 2023 and June 2024. It cannot be reproduced exactly from later CRFs because the EPA recalculates its series each year (nearest: 2021 of the 2024 submission, -370.84). A first refresh used the 2025 submission, 2019-2023 (-394.70); it was superseded the same day when the 2026 submission was used instead. Replacing -371.985 by -392.73 moved the goblin_lite national baseline CO2 total from 3,785.6 to 3,711.0 kt (-2.0%) and the 2050 scenarios from 4,637.5 and 4,640.5 to 4,621.7 and 4,624.9 kt (-0.3%).

## ef_co2_implied_forest_to_grassland_SOC_per_ha

| | |
|---|---|
| Value | **+3,285.34** kg CO2 per hectare of forest converted to grassland per year (3,285.338...; positive = emission) |
| Used by | **Nothing at present.** Forest to grassland uses the Tier 1 calculation in `land_classes/soc.py`. Kept so it can be used or ignored later without re-deriving it |
| Inventory category | CRT 4.C.2 Land converted to grassland, mineral soils (in Ireland this is forest land only, 4.C.2.a) |
| Source data | CRT Table 4.C, **2026 submission**, years 2020-2024 |
| Derivation | **sum of kt CO2 / sum of mineral area (kha) x 1000** over 2020-2024: 139.63 kt / 42.50 kha = 3,285.34 kg CO2/ha/yr |
| What the inventory does | It applies one **constant** rate in every year: a loss of 0.896 t C/ha/yr from mineral soil, i.e. 17.9 t C/ha over the 20-year transition. The 2020-2024 average therefore equals each yearly value |
| Test | `tests/implied_factor_test.py` |
| Derived | November 2026 |

**Worked numbers, 4.C.2 (land converted to grassland: forest, mineral soils).**

| Year | Area within the 20-year transition (kha) | Soil C change, CRT sign (kt C) | kt CO2 (package sign) | kg CO2/ha/yr |
|---|---|---|---|---|
| 2020 | 9.5428 | -8.5504 | 31.3513 | 3,285.34 |
| 2021 | 9.2000 | -8.2432 | 30.2251 | 3,285.34 |
| 2022 | 8.8190 | -7.9018 | 28.9734 | 3,285.34 |
| 2023 | 8.0550 | -7.2173 | 26.4634 | 3,285.34 |
| 2024 | 6.8843 | -6.1683 | 22.6173 | 3,285.34 |
| **Sum** | **42.5011** | **-38.0810** | **139.6305** | **3,285.3384** |

Each year's rate is the same, 0.896 t C/ha/yr: the inventory applies one constant rate to forest land converted to grassland. The area column is the area still inside its 20-year transition (the NID applies the default 20-year period, p.236), which is why it rises to 9.5 kha around 2020 and then falls as the 1990s conversions leave the window.

**Caveats.**
- The area is the area of forest converted to grassland within the 20-year transition period (6.88 kha in 2024; 9.54 kha in 2020), not an annual flow.
- The previous value, +785.79 (`NIR, 2024`), was derived by the database author from an earlier CRF and cannot be reproduced. It is superseded.
- This is an emission. The package's own Tier 1 calculation gives a removal (-7.35 t C/ha, opposite sign). See D4b in `README.md`; the gap is recorded as an expected-failure test in `tests/soc_inventory_test.py`.
- The NID's Tier 2 parameters (Tables 6.20, 6.21) are not used by this factor. Reproducing 0.896 t C/ha/yr from them has not been done.

## Cross-checks of the forest to grassland rate (is +3,285 kg CO2/ha/yr plausible?)

It is high compared with the grassland sink (0.107 t C/ha/yr gained), and it is the opposite sign to the package's Tier 1 calculation. Four checks say it is the inventory's own number and is of a sensible size:

1. **It adds up to the NID's published deforestation total.** NID 2026 Table 6.19 (p.238), column "Mineral Soils, Net" (kt C, all deforestation destinations), 2022: **-13.35**. From the CRT 2026, 2022: grassland -7.9018 + settlements -2.8100 + other land -2.6400 = **-13.3518** kt C. It matches in 2010 (-11.00), 2015 (-13.22), 2020 (-14.08) and 2022 (-13.35). Grassland is 59% of the deforestation soil loss in 2022. (Table 6.19 has the 2024 row repeating the 1990 row, a typing error in the NID; the CRT is used for 2024.)
2. **It is the same order as the NID's own conservative rule.** For settlements and other land the NID assumes 20% of a 110 t C/ha soil stock is lost over 20 years (p.239) = 1.1 t C/ha/yr. The CRT's other-land row is exactly -1.1 t C/ha/yr (-1.32 kt C on 1.2 kha, 2024). The grassland rate, 0.896, is 81% of that.
3. **As a share of the soil stock** the 20-year loss is 17.9 t C/ha against a forest soil stock of about 104.5 t C/ha (Tier 2 mean SOCref 100.46, Table 6.20, times the mean forest FLU 1.04, Table 6.21) = 17%, close to the NID's 20% rule.
4. **It lies inside the Tier 2 range.** Per soil group the 20-year change from forest to grassland is between -57 and +31 t C/ha (Tables 6.20 and 6.21; see `artifacts/soc/repro/d4b_tier2.py`). 17.9 is inside it. I have **not** reproduced the 0.896 t C/ha/yr from the Tier 2 tables: that needs the soil-group split of Irish deforested land, which the NID does not publish.

So the rate is the inventory's own, consistent with its totals and with its other deforestation rates. What is not documented in the NID is exactly how the 0.896 was built from the Tier 2 parameters.

## ef_co2_implied_wilfire_forest, ef_CH4_implied_wilfire_forest, ef_n2o_implied_wilfire_forest

Values 219,392.6 (CO2), 1,793.4 (CH4) and 10.4615 (N2O) kg per hectare burnt. Source `NIR, 2024`; derived by the database author from the inventory's forest fire emissions divided by area burnt. **The derivation is not yet documented.** They are live in the goblin_lite totals and will be reviewed with the fire set of fixes.

## ef_co2_forest_to_settlement_mineral_soil

80,666.67 kg CO2 per hectare, **one-off over 20 years**, not per year. This is a rule, not an implied value: 20% of a 110 t C/ha stock is emitted over 20 years (NID s.6.3.6.2, p.239) = 22 t C = 80,667 kg CO2. Not reachable from the goblin_lite totals.

## To refresh a soil factor
1. Put the new submission's yearly CRT workbooks in a folder and run `python tools/extract_crt_table4c.py <folder> <submission> tests/data/inventory/crt<submission>_4c_mineral_soils.csv`.
2. Run `python tools/derive_implied_grassland_factor.py <submission> <first_year> <last_year>`.
3. Update the database value and the `source` row (update only the row with `ef_country = 'ireland'` for the value and `'source'` for the source; the table has three rows).
4. Update the numbers on this page, the constants in `tests/implied_factor_test.py`, `tests/soc_inventory_test.py` and the national totals in `tests/soc_test.py`, `CHANGELOG.md` and the emission-factor inventory.

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

## ef_co2_implied_wildfire_forest, ef_ch4_implied_wildfire_forest, ef_n2o_implied_wildfire_forest

Forest wildfire factors, kg CO2 / CH4 / N2O per ha burnt (FIRE-1). Renamed from `ef_co2_implied_wilfire_forest`,
`ef_CH4_implied_wilfire_forest`, `ef_n2o_implied_wilfire_forest` (nothing outside this package read them).

| factor | value | before FIRE-1 |
|---|---|---|
| CO2 | 104,427.25 | 219,392.6 |
| CH4 | 312.82 | 1,793.4 |
| N2O | 17.3047 | 10.4615 |

- **Derivation:** sum over 2020-2022 of CRT 2026 Table 4(IV) 4.A.1 + 4.A.2 wildfire emissions / sum over 2020-2022 of
  CRF 2024 Table4(V) area burnt, 4.A.1 + 4.A.2 (499.88 ha). The CRT 2026 leaves area burnt blank, so the previous
  submission's area is the latest published one. Script: `tools/derive_implied_forest_fire_factor.py` (reads the
  fixtures in `tests/data/inventory/`; `--write` sets the value, `source` and `units` cells). Test: `tests/forest_fire_factors_test.py`.
- **Method behind the inventory values** (NID 2026 s.6.3.4.4, IPCC 2006 eq 2.27): dry matter x Cf 0.45 x Gef
  (CO2 1,569, CH4 4.7, N2O 0.26 g/kg; the NID text prints N2O as 0.026, the CRT values need 0.26). Dry matter 177,713 kg/ha
  (4.A.1) and 103,485 kg/ha (4.A.2), so 125,474 and 73,066 kg CO2/ha. The CRT 2026 values per category are 123,857-124,232
  and 74,433-74,567 kg CO2/ha in 2020-2022. The total-forest factor depends on the 4.A.1/4.A.2 mix of the burnt area
  (0.59-0.64 in these years).
- **The old values** were not one calculation: CO2 was the CRF 2024 total-forest implied factor, CH4 and N2O the sum of
  the 4.A.1 and 4.A.2 factors. Against the inventory: 2.10x, 5.73x and 0.60x.
- **Input expected:** `share_burnt` is the **total** forest burnt area (4.A.1 + 4.A.2). landcover_assignment currently
  supplies 4.A.1 only (logged for that package; not compensated here).
- **To refresh:** re-extract the fixtures from a newer submission (`tools/extract_inventory_fixtures.py`), change `YEARS`
  in the script, run it with `--write`, update this section and the test.

## N2O from the loss of soil carbon (constants in `lca_emission.py`)

Used by `mineral_soils_n2o_from_forest_to_grassland` through `n2o_from_soil_carbon_loss`. The unit returned is **kg N2O per year**. goblin_lite multiplies by 1e-6 (to kt) and applies the global warming potential itself.

| Step | Formula | Constant | Source |
|---|---|---|---|
| 1. Nitrogen mineralised with the carbon lost | N (kg) = soil C lost (t C) x 1000 / **15** | C:N ratio 15 (`C_to_N = 1/15`) | NID 2026 p.239 (deforestation). CRT Table 4(III) agrees: 7,901.8 t C lost in 2022 / 15 = 526.8 t N, the CRT's value. (Agricultural soils use 10, NID section 5.5; not used here) |
| 2. Direct N2O-N | N x **EF1 = 0.006** | `EF1_SOM` | IPCC 2019 Refinement, Table 11.1, wet climate. It is not stated in the NID text, but is what the CRT and NID Table 6.9 use: 526.8 t N x 0.006 x 44/28 = 4.97 t N2O, the CRT's 0.00497 kt |
| 3. Indirect N2O-N | N x **FracLEACH 0.1** x **EF5 0.011** | `FRAC_LEACH`, `EF5` | NID Table 5.7 (FracLEACH-(H) 0.1) and p.185 (EF5 0.011): 526.8 x 0.1 x 0.011 x 44/28 = 0.91 t N2O, the CRT's 0.00091 kt |
| 4. N2O-N to N2O | x **44/28** | `N2O_N_to_N2O` | molecular weights |
Per kg of N mineralised: (0.006 + 0.1 x 0.011) x 44/28 = **0.011157 kg N2O**. Per tonne of soil carbon lost: 1000/15 x 0.011157 = **0.7438 kg N2O**; with the AR5 GWP of 265 (used by the NID) that is 0.197 t CO2e per t C. The previous code returned t C / 15 as if it were kg N2O, which is 1000 x 0.011157 = **11.157 times smaller** than this.

**Check.** `tests/soc_n2o_test.py` takes the CRT 2026 Table 4(III) row 4(III).C.2.a, `N mineralised`, and compares the package's value with the CRT total N2O in the 22 years with a CRT total of at least 0.002 kt: the package matches to the rounding of the CRT. The fixture is `tests/data/inventory/crt2026_4iii_forest_to_grassland_n2o.csv` (written by `tools/extract_crt_table4c.py`). The CRT also confirms the NID's own forest table: NID Table 6.9 (forest remaining forest) gives direct N2O of 0.024 kt for 2,564.8 t N in 1990 = EF1 0.006, and total 7.583 kt CO2e = 28.6 t N2O x GWP 265.

| Year | N mineralised (t N) | CRT direct (kt N2O) | CRT indirect (kt N2O) | CRT total (kt N2O) | Package (kt N2O) |
|---|---|---|---|---|---|
| 2020 | 570.02 | 0.00537 | 0.00099 | 0.00636 | 0.00636 |
| 2021 | 549.55 | 0.00518 | 0.00095 | 0.00613 | 0.00613 |
| 2022 | 526.79 | 0.00497 | 0.00091 | 0.00588 | 0.00588 |
| 2023 | 481.15 | 0.00454 | 0.00083 | 0.00537 | 0.00537 |
| 2024 | 411.22 | 0.00388 | 0.00071 | 0.00459 | 0.00459 |

**Assumptions.** The inventory counts only losses of soil carbon for deforestation. The package's function is linear, so a gain of soil carbon (which the Tier 1 forest to grassland calculation gives, see D4b) gives a negative N2O (immobilisation). The sign question disappears if D4b is ever aligned with the inventory.

## N2O from drained organic soils (`ef_n2o_*_drainage_*`)

These factors are stored in **kg N2O per ha per year**: the published kg N2O-N value times 44/28 (1.5714). The conversion was made when the database was built; the code multiplies area by the factor and does not convert again. Checked by `tests/n2o_drainage_factors_test.py`.

| Column | Stored | Published (kg N2O-N/ha/yr) | Source |
|---|---|---|---|
| `ef_n2o_grassland_drainage_poor` | 6.757 | 4.3 | NID 2026 s.5.6.1 p.183 and Table 5.6 (EF2); IPCC 2013 Wetlands Supplement Table 2.5 |
| `ef_n2o_grassland_drainage_rich` | 12.886 | 8.2 | same |
| `ef_n2o_forest_drainage_rich` | 4.4 | 2.8 | NID 2026 s.6.3 p.220; IPCC 2013 Wetlands Supplement Table 2.5 |
| `ef_n2o_forest_drainage_poor` | 1.1 | 0.7 | NID 2026 s.6.3 p.220 (country specific, Yamulki et al. 2013); the NID text writes "0.7 kg N2O" but the inventory treats it as N2O-N (CRT implied EF 1.115 kg N2O-N/ha for forest is a mix of 2.8 and 0.7) |
| `ef_n2o_wetland_drainage_default` | 0.4714 | 0.3 | NID 2026 s.6.6 p.280 (industrial and domestic peat extraction); IPCC 2013 Wetlands Supplement, drained peatland managed for extraction, boreal/temperate |

Matches the inventory, no method deviation:
- CRT 2026 Table 3.D, row 3.D.1.f (cultivation of organic soils, i.e. drained organic grassland), 2022: 141,000 ha x 6.052 kg N2O-N/ha x 44/28 = 1.341 kt N2O. 6.052 is the mix of 4.3 and 8.2 at 44.9% nutrient-rich.
- CRT 2026 Table 4(II).D.1.a, drained peat extraction, 2020 and 2022: EF 0.3 kg N2O-N/ha; N2O = area x 0.3 x 44/28 (domestic 83.93 kha gives 0.03957 kt; industrial 41.68 kha gives 0.01965 kt).
- The package applies the wetland factor to domestic plus industrial drained area (`wetland.py` `drainage_n2o_organic_soils`), the same area as the CRT.
- Grassland drained-organic N2O is reported in CRT Table 3.D, not in Table 4(II) (cell empty there).
- NID 2024 and NIR 2024 are the same document (the EPA renamed National Inventory Report to National Inventory Document).

## ef_co2_forest_to_settlement_mineral_soil

80,666.67 kg CO2 per hectare, **one-off over 20 years**, not per year. This is a rule, not an implied value: 20% of a 110 t C/ha stock is emitted over 20 years (NID s.6.3.6.2, p.239) = 22 t C = 80,667 kg CO2. Not reachable from the goblin_lite totals.

## Inventory alignment fixtures (tests only)

These files are test inputs and expected values for `tests/inventory_alignment_test.py`; no factor in the database is derived from them.

| File | Source | Years | How it is made |
|---|---|---|---|
| `tests/data/inventory/crt2026_lulucf.csv` | EPA CRT 2026 (`IRL-CRT-2026-V1.0-<year>.xlsx`): Table4, Table4.A-D, Table4(II), Table4(IV) | 2020-2024 | `tools/extract_inventory_fixtures.py`; each cell is found by sheet, row and column, and the row label is checked |
| `tests/data/inventory/crf2024_burnt_area.csv` | EPA CRF 2024 submission, Table4(V) area burnt (col E, ha) | 2020-2022 | same tool. The CRT 2026 leaves area burnt blank, so this earlier submission is the only published area |
| `tests/data/inventory/nid2026_forest_organic_soils.csv` | NID 2026 Table 6.7 (p.217, 4.A.1) and Table 6.15 (p.231, 4.A.2) | 2020-2024 | transcribed by hand: drained N-poor and N-rich (organo-mineral) areas, on-site and DOC |

Notes on the sources:
- NID 2026 Table 6.8 (forest burnt area): the rows labelled 2020-2024 are CRT years 2016-2020 (e.g. 22.00 kt CO2 in the "2024" row is CRT 2020). There is no forest burnt area for CRT 2021-2024.
- CRT 4.A col T (organic soil C) is NID on-site + DOC; CRT 4(II) col H CO2 is DOC only.
- CRT 4(II).C.1 "Other organic soils" is the package's rewetted grassland (NID 2026 s.6.5.2).
- Table4(II) and Table4.D split the peat-extraction areas differently (2020 industrial: 55.5 kha and 98.3 kha). The inputs use 4(II).

## To refresh a soil factor
1. Put the new submission's yearly CRT workbooks in a folder and run `python tools/extract_crt_table4c.py <folder> <submission> tests/data/inventory/crt<submission>_4c_mineral_soils.csv`.
2. Run `python tools/derive_implied_grassland_factor.py <submission> <first_year> <last_year>`.
3. Update the database value and the `source` row (update only the row with `ef_country = 'ireland'` for the value and `'source'` for the source; the table has three rows).
4. Update the numbers on this page, the constants in `tests/implied_factor_test.py`, `tests/soc_inventory_test.py` and the national totals in `tests/soc_test.py`, `CHANGELOG.md` and the emission-factor inventory.

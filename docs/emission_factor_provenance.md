# Provenance of the implied emission factors

An **implied** emission factor is worked back from reported inventory totals (kt CO2 divided by area). It is not a measured or default IPCC value. This page records, for each implied factor in the database
(`src/landcover_lca/database/landcover_lca_database.db`, table `emission_factors_land_use`), where it came from, how it was derived, and how to refresh it. The database also holds a `source` row and a `units` row under each factor; the `units` labels are legacy and not reliable (the unit is stated here).

**Source data for the two soil factors:** EPA CRT Table 4.C (Grassland), **2026 submission**, one workbook per year 1990-2024 (`IRL-CRT-2026-V1.0-<year>.xlsx`). The mineral-soil rows are extracted by `tools/extract_crt_table4c.py` into `tests/data/inventory/crt2026_4c_mineral_soils.csv`. CRT sign convention: + = gain of carbon, - = loss. The extract flips it to the package convention (+ emission, - removal): kg CO2/ha = -(t C/ha) x 1000 x 44/12. The 4.C.1 rows reproduce the NID 2026 key category table (+107.27 kt CO2 in 1990, -1,549.47 kt CO2 in 2024).

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

**Caveats.**
- The area is the area of forest converted to grassland within the 20-year transition period (6.88 kha in 2024; 9.54 kha in 2020), not an annual flow.
- The previous value, +785.79 (`NIR, 2024`), was derived by the database author from an earlier CRF and cannot be reproduced. It is superseded.
- This is an emission. The package's own Tier 1 calculation gives a removal (-7.35 t C/ha, opposite sign). See D4b in `README.md`; the gap is recorded as an expected-failure test in `tests/soc_inventory_test.py`.
- The NID's Tier 2 parameters (Tables 6.20, 6.21) are not used by this factor. Reproducing 0.896 t C/ha/yr from them has not been done.

## ef_co2_implied_wilfire_forest, ef_CH4_implied_wilfire_forest, ef_n2o_implied_wilfire_forest

Values 219,392.6 (CO2), 1,793.4 (CH4) and 10.4615 (N2O) kg per hectare burnt. Source `NIR, 2024`; derived by the database author from the inventory's forest fire emissions divided by area burnt. **The derivation is not yet documented.** They are live in the goblin_lite totals and will be reviewed with the fire set of fixes.

## ef_co2_forest_to_settlement_mineral_soil

80,666.67 kg CO2 per hectare, **one-off over 20 years**, not per year. This is a rule, not an implied value: 20% of a 110 t C/ha stock is emitted over 20 years (NID s.6.3.6.2, p.239) = 22 t C = 80,667 kg CO2. Not reachable from the goblin_lite totals.

## To refresh a soil factor
1. Put the new submission's yearly CRT workbooks in a folder and run `python tools/extract_crt_table4c.py <folder> <submission> tests/data/inventory/crt<submission>_4c_mineral_soils.csv`.
2. Run `python tools/derive_implied_grassland_factor.py <submission> <first_year> <last_year>`.
3. Update the database value and the `source` row (update only the row with `ef_country = 'ireland'` for the value and `'source'` for the source; the table has three rows).
4. Update the numbers on this page, the constants in `tests/implied_factor_test.py`, `tests/soc_inventory_test.py` and the national totals in `tests/soc_test.py`, `CHANGELOG.md` and the emission-factor inventory.

# Provenance of the implied emission factors

An **implied** emission factor is worked back from reported inventory totals (kt CO2 divided by area). It is not a measured or default IPCC value. This page records, for each implied factor in the database
(`src/landcover_lca/database/landcover_lca_database.db`, table `emission_factors_land_use`), where it came from, how it was derived, and how to refresh it. The database also holds a `source` row and a `units` row under each factor; the `units` labels are legacy and not reliable (the unit is stated here).

## ef_co2_implied_grassland_remaining_SOC_per_ha

| | |
|---|---|
| Value | **-394.70** kg CO2 per hectare of mineral grassland per year (-394.70054675...; negative = removal) |
| Used by | `Grassland.mineral_co2_in_grassland` (`land_classes/grassland.py`): mineral grassland area x this factor, every year and scenario. The only SOC term in the goblin_lite national case |
| Inventory category | CRF 4.C.1 Grassland remaining grassland, mineral soils (NID 2026 s.6.5; Tier 1) |
| Source data | EPA CRF Table 4.C, **2025 submission**, years 2019-2023, stored in `tests/data/inventory/crf_4c1_grassland_remaining_mineral.csv` |
| Derivation | **sum of kt CO2 / sum of mineral area (kha) x 1000** over 2019-2023: -7,655.64 kt / 19,396.06 kha = -394.70 kg CO2/ha/yr |
| Yearly values | 2019 -408.44, 2020 -385.45, 2021 -390.73, 2022 -390.98, 2023 -397.90 |
| Script | `tools/derive_implied_grassland_factor.py` (reproduces the value) |
| Test | `tests/implied_factor_test.py` recomputes the value from the stored extract and checks the database |
| Derived | November 2026, replacing the earlier value below |

**Why a five-year average of the latest submission.** The EPA recalculates the whole time series every submission, so a single year is not stable. A baseline year is usually 2020 but not always, so the factor should represent recent conditions, not one year. Pooling kt and area weights each year by its area.

**Assumptions to be aware of.**
- The constant is applied to every year of every scenario, including years after the inventory. The sink continuing unchanged is a modelling assumption, not an inventory fact. The inventory series is not constant: it runs from about +27 kg/ha (1990) to about -400 (2018-2023), driven mainly by the shift from improved grassland to rough grazing (NID s.6.5.2.4).
- The NID publishes only totals for this category (+107.27 kt in 1990; -1,549.47 kt in 2024), not a per-hectare factor or a mineral-area table, so a derived value is needed.
- The package's mineral grassland area (3,595.7 kha in the goblin_lite 2020 baseline) is 7.3% below the inventory's (3,880.7 kha). The factor is not the cause; the area comes from landcover_assignment.

**Previous value: -371.985** (`NIR, 2024`). Derived by the database author from the CRF, added between June 2023 and June 2024. It cannot be reproduced exactly from the 2024 or 2025 CRF because the EPA recalculates its series every year. The nearest inventory values are 2021 of the 2024 submission (-370.84) and the 2019-2022 mean (-372.08). Replacing it moved the goblin_lite national baseline CO2 total from 3,785.6 to 3,703.9 kt (-2.2%) and the 2050 scenarios from 4,637.5 and 4,640.5 to 4,620.2 and 4,623.5 kt (-0.4%).

**To refresh.** Put the new submission's CRF 4.C.1 rows in the fixture, run `python tools/derive_implied_grassland_factor.py <submission> <first_year> <last_year>`, update the database value and the `source` row, update the numbers on this page and in `tests/implied_factor_test.py`, and note the change in `CHANGELOG.md`.

## ef_co2_implied_forest_to_grassland_SOC_per_ha

| | |
|---|---|
| Value | +785.79 kg CO2 per hectare per year (positive = emission) |
| Used by | **Nothing at present.** Forest to grassland uses the Tier 1 calculation in `land_classes/soc.py` |
| Inventory category | CRF 4.C.2.1 Forest land converted to grassland, mineral soils |
| Source | `NIR, 2024`. Derived by the database author from the CRF; the exact derivation is not reproducible from the current CRF |
| Status | Kept, because it may be the intended basis for forest to grassland. **Unverified.** In the 2024-submission extract the per-hectare values for this row are 244 (1990-2005), 1,509 (2010), 862 (2020), 796 (2022); the 2025-submission rows for this category are corrupted (NaN or about -9,978) and cannot be used. Whether the area column is annual or accumulated over 20 years has not been checked |
| Related | D4b: the NID's own Tier 2 parameters (Tables 6.20, 6.21) are not used by this factor |

## ef_co2_implied_wilfire_forest, ef_CH4_implied_wilfire_forest, ef_n2o_implied_wilfire_forest

Values 219,392.6 (CO2), 1,793.4 (CH4) and 10.4615 (N2O) kg per hectare burnt. Source `NIR, 2024`; derived by the database author from the inventory's forest fire emissions divided by area burnt. **The derivation is not yet documented.** They are live in the goblin_lite totals and will be reviewed with the fire set of fixes.

## ef_co2_forest_to_settlement_mineral_soil

80,666.67 kg CO2 per hectare, **one-off over 20 years**, not per year. This is a rule, not an implied value: 20% of a 110 t C/ha stock is emitted over 20 years (NID s.6.3.6.2, p.239) = 22 t C = 80,667 kg CO2. Not reachable from the goblin_lite totals.

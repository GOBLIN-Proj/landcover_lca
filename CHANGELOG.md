# Changelog

All notable changes to `landcover_lca` are recorded here, newest first. Format follows
[Keep a Changelog](https://keepachangelog.com/). Each SOC fix is tracked as a numbered
dossier (D1, D2, ...) in `artifacts/soc/` (local working folder, not in the repository).

## [Unreleased]

### Changed
- **FIRE-1: forest wildfire factors replaced with the 2020-2022 inventory values (changes results).** The three factors
  did not reproduce the inventory (2.10x CO2, 5.73x CH4, 0.60x N2O on the inventory's own areas): CO2 was the CRF 2024
  total-forest factor, CH4 and N2O the sum of the two forest category factors. New values, kg per ha burnt: CO2
  219,392.6 -> 104,427.25, CH4 1,793.4 -> 312.82, N2O 10.4615 -> 17.3047 (CRT 2026 4(IV).A / CRF 2024 area burnt,
  2020-2022, sum/sum). Scripted (`tools/derive_implied_forest_fire_factor.py`) and documented in
  `docs/emission_factor_provenance.md`; `source` and `units` cells now state the tables, years and unit.
  - Database columns renamed: `ef_{co2,ch4,n2o}_implied_wildfire_forest` (were `ef_co2_implied_wilfire_forest`,
    `ef_CH4_implied_wilfire_forest`, `ef_n2o_implied_wilfire_forest`); both `forestland.py` (main and geo_goblin) read
    the new names, and their docstrings now describe what the code does.
  - goblin_lite national case (177.65 ha burnt, every scenario): CO2 -20.42 kt (3,711.0 -> 3,690.6 kt baseline),
    CH4 -263 t, N2O +1.22 t. geo_goblin uses the same database and moves the same way.
  - Tests: `tests/forest_fire_factors_test.py` (new, in CI); forest fire rows in `inventory_alignment_test` now covered
    (within 1.6% each year); goblin_lite totals re-pinned in `soc_test` and `soc_n2o_test`.

### Added
- **Inventory alignment tests** (`tests/inventory_alignment_test.py`, in CI). The package is given the
  NID/CRT 2026 areas and each emission term is compared with the CRT 2026 emissions, 2020-2024
  (fire 2020-2022). No change to `src/` or to any result.
  - Fixtures in `tests/data/inventory/`, each value with its source; `tools/extract_inventory_fixtures.py`
    rebuilds the CRT/CRF ones. `openpyxl` is added as a Poetry dev dependency for the extraction tools.
  - `inventory_coverage.csv` marks each comparison covered, gap (expected failure, with its fix) or excluded.
  - Covered (10): forest drainage CO2 (2020-2023), CH4, N2O; grassland remaining mineral CO2 (2020-2024 sum);
    grassland organic CO2; grassland drainage and rewet-status CH4 (consistency only); peat extraction N2O;
    near-natural CH4; wetland rewetted CH4 (sum).
  - Gaps (14): fire in all land uses (FIRE-1, FIRE-2, wetland), wetland drainage and rewetted CO2, industrial
    peat CH4 (wetland, P1).

## [0.3.0] - 2026-11-17

This release changes results. It is a minor version bump on purpose: goblin_lite pins
`landcover_lca ^0.2.0`, which excludes 0.3.0, so goblin_lite keeps its current numbers
until it is deliberately moved (separate job, after the data audit). Nothing is released to
PyPI by this entry; it records what the merge of branch `soc-review` contains.

Summary of what changes numbers:
- D7 (implied soil factors refreshed from the 2026 CRT): goblin_lite national baseline CO2
  3,785.6 -> 3,711.0 kt (-2.0%); 2050 scenarios -0.3%.
- D1, D2, D4a, D5: only for scenarios that convert land into cropland or grassland (none of
  goblin_lite's current scenarios do). D1 and D2 ship together: D1 alone returns numbers
  that are in t C per year, not kg CO2.
- D3, D4b, D4c, D6: a clearer error and documentation, no change to results.
- CROP-1 (cropland change): documented and locked by `tests/cropland_readiness_test.py`; no result change.
- Not in this release: D8 (geo_goblin
  still carries the old SOC code).
- CI now also runs `soc_test`, `soc_inventory_test`, `soc_n2o_test`, `transition_key_test` and
  `implied_factor_test`, `n2o_drainage_factors_test`, `time_period_test` and `cropland_readiness_test` (`.github/workflows/main.yml`). `load_test` stays out: it already fails.

### Fixed
- **D2 / S2: mineral-soil CO2 from land-use change was in t C, not kg CO2.**
  The six `mineral_soils_co2_from_<past>_to_<current>` functions in `lca_emission.py`
  now return **kg CO2 per year**: the `SOC` class result (t C/yr) x 1000 x 44/12
  (new constant `C_to_CO2`). Every other term in `total_co2_emission` was already kg CO2,
  and goblin_lite multiplies the total by 1e-6 to give kt, so SOC conversion terms were
  too small by 3,666.67. Example: 1,000 ha grassland to cropland over 30 years was
  1,102.65 (reported as 0.0011 kt) and is now 4,043,050 kg CO2 (4.04 kt). Sign unchanged.
  - The `SOC` class still returns t C/yr (its docstring says so).
  - `mineral_soils_n2o_from_forest_to_grassland` is unchanged (D5).
  - goblin_lite national case (2020-2050): no change in any total (the SOC conversion
    areas are zero there); the three cropland CO2 cells now print as `0.0` instead of `0`.
  - **Behaviour change for any scenario that converts land into cropland or grassland:**
    totals rise by the corrected amount. Release D1 and D2 together.
- **D1 / S1: mineral-soil SOC change returned `None` for spans of 20 years or less.**
  `SOC.compute_emissions_from_mineral_soils_in_land_use_change`
  (`land_classes/soc.py`) now returns
  `annual_area x min(year_range, 20) x (SOC_past - SOC_current) / 20`
  (NID 2026 eq 6.4.3, transition period T = 20 years). Before, when the span between
  the land-use year and the baseline year was 20 years or less and the converted area was
  non-zero, the function returned `None`. That raised a `TypeError` in
  `total_co2_emission_cropland`, `total_co2_emission_to_grassland`,
  `total_n2o_emission_grassland`, `total_co2_emission` and `total_n2o_emission`.
  - Spans over 20 years give the same values as before.
  - Spans of 1 to 20 years now return a number (for example 1,653.975 t C/yr for
    1,000 ha of grassland to cropland, any span from 1 to 20).
  - Zero converted area and a zero span (the baseline call) still return 0.
  - Results are still in t C per year; the unit conversion is D2.
  - goblin_lite national case (2020-2050): no change in any output.

### Changed (validation)
- **D6 / S8: the span between the baseline and the evaluated year is read in one place and validated.**
  `SOC.get_time_period` and `LandUse.get_time_period` were identical copies; both now call `models.get_time_period(land_use_data, past_land_use_data, current_land_use, past_land_use)`. The value is unchanged for correct data (year of the destination category in the target dataset minus the same in the baseline). New errors replace a bare `AttributeError` and a silently wrong span: `KeyError` naming the dataset and listing the categories present if the destination category is missing; `ValueError` if the source category carries a different year from the destination within the same dataset (a source category absent from the dataset cannot be compared and is not an error). goblin_lite national output identical (checked byte for byte). `tests/time_period_test.py`.

### Documented
- **CROP-1: grassland to cropland works end to end and its assumptions are written down (LA1, CR2, NI1, CR1, GR1).** No code or result change. New README section "Cropland change: what the package assumes" and `tests/cropland_readiness_test.py` (11 tests: 100,000 ha over 30 years = 467.5 kt CO2/yr, 15- and 20-year spans, other land uses unchanged). Recorded: cropland only grows and only `Grassland_to_*` is written by `landcover_assignment` (`abs()` direction quirk, fix belongs there); new cropland is mineral so no organic-cropland term (CR2); all converted grassland is taken as improved, 1.14, with the sensitivity (3.1% lower emission per 10% unimproved) and the unused Table 6.31 factors kept for a future partition (GR1); the inventory has no conversion to cropland (CRT 4.B.2 = NO) so there is no total to match (NI1); cropland remaining cropland (CRT 4.B.1) is the net of crop and temporary-grass rotation, is not modelled and is not a fixed-factor term (CR1).
- **EF2: the N2O drainage factors are in kg N2O, not kg N2O-N, and match the inventory.** The five `ef_n2o_*_drainage_*` factors are the published N2O-N values x 44/28 (grassland 4.3 and 8.2, forest 2.8 and 0.7, wetland 0.3: NID 2026 pp.183, 220, 280) and reproduce CRT 2026 Table 3.D and 4(II). No change to any result. Database `units` cells corrected from "N20/kg" to "kg N2O/ha/yr" and `source` cells give the NID page; `tests/n2o_drainage_factors_test.py`; `docs/emission_factor_provenance.md`.
- **D4c:** land leaving grassland is assumed to be mineral soil and no mineral share is applied (soil type of the converted hectares is unknown; NID s.6.4.6). In GOBLIN scenarios the converted land is mineral grassland moving to another use; rewetting of drained organic grassland is a change in the grassland's soil shares, not a conversion. The assumption does not hold for land moving into grassland (forest or cropland to grassland): organic hectares there would be charged twice. Stated in the `SOC` docstring and the README; the leaving-grassland case is recorded by `TestConvertedAreaIsAssumedMineral`. No change in behaviour.
- **D4b:** forest to grassland soil carbon is a known simplification and is not changed. The package
  gives -7.35 t C/ha over 20 years (SOCref 73.51 x (1.04 - 1.14)), a removal; the inventory (CRT 2026
  4.C.2, Tier 2 soil-group values, NID Tables 6.20, 6.21) reports an emission of +17.9 t C/ha over 20 years
  (0.896 t C/ha/yr). The signs differ.
  GOBLIN cannot reach it (landcover_assignment writes only `Grassland_to_*` columns). Recorded in the
  README, the `SOC` docstring and an expected-failure test in `tests/soc_inventory_test.py`.
- **D1:** `compute_emissions_from_mineral_soils_in_land_use_change` docstring now states
  that the result is a snapshot at the evaluated year (`year_range` is the elapsed time
  from the baseline, not a loop over years), that conversion is assumed to occur in
  equal annual cohorts, and that this assumption only affects spans over 20 years
  (for 1,000 ha over 30 years: 1,102.65 even split, 1,653.97 if all converted in the
  last 5 years, 0 if all in the first 5 years, in t C/yr). Real conversion timing would
  need year-by-year data from landcover_assignment.

### Changed
- **D5 / S5: N2O from soil carbon loss (forest to grassland) now follows the inventory chain.**
  `mineral_soils_n2o_from_forest_to_grassland` returned `t C / 15`, which is tonnes of nitrogen, as if it
  were kg N2O, with no emission factor, no 44/28 and no indirect N2O. It now returns kg N2O per year:
  `t C x 1000 / 15 x (EF1 0.006 + FracLEACH 0.1 x EF5 0.011) x 44/28` (new helper
  `n2o_from_soil_carbon_loss`, constants `EF1_SOM`, `FRAC_LEACH`, `EF5`, `N2O_N_to_N2O`), NID 2026 eq 11.8
  and 11.10. The value is **11.157 times** the previous one. Reproduces CRT 2026 Table 4(III), row
  4(III).C.2.a (forest land converted to grassland) in every year (22 years checked, `tests/soc_n2o_test.py`).
  goblin_lite national case: no change (the conversion area is zero). Behaviour change for any scenario
  that converts forest to grassland (none can today: landcover_assignment never writes `Forest_to_*`).
- **D7: the implied soil factors are refreshed from the 2026 CRT and documented.**
  `ef_co2_implied_grassland_remaining_SOC_per_ha`: -371.985 -> **-392.73 kg CO2/ha/yr**
  (CRT 4.C.1 mineral soils, 2026 submission, 2020-2024, sum kt CO2 / sum mineral area).
  `ef_co2_implied_forest_to_grassland_SOC_per_ha` (unused): 785.79 -> **+3,285.34 kg CO2/ha/yr**
  (CRT 4.C.2, same window; the inventory applies a constant 0.896 t C/ha/yr loss).
  The old values were derived from earlier CRFs by the database author (`NIR, 2024`) and cannot be
  reproduced because the EPA recalculates its series each year. Extraction and derivation are scripted
  (`tools/extract_crt_table4c.py`, `tools/derive_implied_grassland_factor.py`), recorded in
  `docs/emission_factor_provenance.md` and tested (`tests/implied_factor_test.py`). **This is the one
  SOC change that alters goblin_lite results:** national baseline CO2 3,785.6 -> 3,711.0 kt (-2.0%);
  2050 scenarios 4,637.5 -> 4,621.7 and 4,640.5 -> 4,624.9 kt (-0.3%). The database `source` cells are updated.
- **D4a: transitions involving cropland now use SOCref LAC = 85 t C/ha (was 73.51).**
  `SOC.compute_SOC_ref_for_land_use` returns the Low Activity Clay value when cropland is
  the past or the current land use (NID 2026 s.6.4.6: 98% of cropland is on LAC soils;
  Table 6.28). With the Table 6.31 factors this reproduces Table 6.32 (58.7 and 69.7 t C/ha).
  All other transitions keep the weighted mean 73.51 until D4b. Cropland SOC changes rise
  by 85 / 73.51 = 1.156: 1,000 ha of grassland to cropland over 30 years is 4.675 kt CO2/yr
  (was 4.043). Converted grassland stays improved grassland (1.14): scenario conversions
  are permanent, not the temporary-grassland rotation of Table 6.32. goblin_lite national
  case: no change, and landcover_assignment only fills `Grassland_to_*` columns, so
  `Forest_to_Cropland` and `Cropland_to_Grassland` are always 0 there.
- **D3 / S6: a missing transition-matrix column now raises a clear `KeyError`.**
  The SOC and land use code (`soc.py`, `landuse.py`) now read transition areas through
  `models.get_transition_area(transition_matrix_data, past, current)`. If the column is
  absent, the error names it and lists the available transition columns, instead of a bare
  `KeyError('forest_to_cropland')`. A missing column is deliberately not treated as zero:
  a renamed or dropped column would silently remove a land use change from the result.
  Only 8 of the 36 columns are read (the four `X_to_X` columns for grassland, wetland,
  cropland and forest, plus grassland/forest to cropland, cropland/forest to grassland).
  Behaviour with a complete matrix is unchanged; goblin_lite national case: no change.
- **D1:** a negative span (land-use year earlier than the baseline year) now raises
  `ValueError` instead of returning `None`.

### Added
- Inventory tests (Layer B): `tests/soc_inventory_test.py` with fixtures in
  `tests/data/inventory/` (NID 2026 Tables 6.28, 6.31, 6.32 and the CRF 4.C.1 grassland
  mineral-soil series). Passing tests: SOCref and adjustment factors in the database match
  the NID; Table 6.32 is reproduced from Tables 6.28 and 6.31, and by the package since D4a; the 2020 baseline for
  grassland remaining grassland is within 4.4% of the 2024 submission. Expected failures
  record known gaps: the 2025-submission baseline is 10.6% away,
  the constant grassland factor cannot follow the inventory time series, and the
  database factor for unmanaged grassland (0.95) differs from NID unimproved (1.0).
- README section "Soil organic carbon (mineral soils): method, units and assumptions",
  including the assumption that all converted grassland is improved grassland (1.14).
- `tests/soc_n2o_test.py` and `tests/data/inventory/crt2026_4iii_forest_to_grassland_n2o.csv`: the N2O chain against CRT Table 4(III).
- `tests/transition_key_test.py`: each of the 8 required columns raises the informative
  error; a column that is never read can be absent without changing results.
- `tests/soc_test.py`: span tests (1 to 60 years), hand-calculated values, comparison
  with the previous loop for spans over 20 years, zero-area, zero-span and negative-span
  cases.

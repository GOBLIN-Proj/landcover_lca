# Changelog

All notable changes to `landcover_lca` are recorded here, newest first. Format follows
[Keep a Changelog](https://keepachangelog.com/). Each SOC fix is tracked as a numbered
dossier (D1, D2, ...) in `artifacts/soc/`. Unreleased entries have not been merged to
`main` or released.

## [Unreleased]

Planned release note: the SOC fixes D1 and D2 ship together. D1 alone makes spans of
20 years or less return a number, but still in t C per year, not kg CO2 (see D2).

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

### Documented
- **D1:** `compute_emissions_from_mineral_soils_in_land_use_change` docstring now states
  that the result is a snapshot at the evaluated year (`year_range` is the elapsed time
  from the baseline, not a loop over years), that conversion is assumed to occur in
  equal annual cohorts, and that this assumption only affects spans over 20 years
  (for 1,000 ha over 30 years: 1,102.65 even split, 1,653.97 if all converted in the
  last 5 years, 0 if all in the first 5 years, in t C/yr). Real conversion timing would
  need year-by-year data from landcover_assignment.

### Changed
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
  the NID; Table 6.32 is reproduced from Tables 6.28 and 6.31; the 2020 baseline for
  grassland remaining grassland is within 4.4% of the 2024 submission. Expected failures
  record known gaps: package SOC loss for temporary grass to cropland is 13% below
  Table 6.32 (SOCref 73.51 against 85), the 2025-submission baseline is 10.6% away,
  the constant grassland factor cannot follow the inventory time series, and the
  database factor for unmanaged grassland (0.95) differs from NID unimproved (1.0).
- README section "Soil organic carbon (mineral soils): method, units and assumptions",
  including the assumption that all converted grassland is improved grassland (1.14).
- `tests/transition_key_test.py`: each of the 8 required columns raises the informative
  error; a column that is never read can be absent without changing results.
- `tests/soc_test.py`: span tests (1 to 60 years), hand-calculated values, comparison
  with the previous loop for spans over 20 years, zero-area, zero-span and negative-span
  cases.

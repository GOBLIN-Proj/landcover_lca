# Changelog

All notable changes to `landcover_lca` are recorded here, newest first. Format follows
[Keep a Changelog](https://keepachangelog.com/). Each SOC fix is tracked as a numbered
dossier (D1, D2, ...) in `artifacts/soc/`. Unreleased entries have not been merged to
`main` or released.

## [Unreleased]

Planned release note: the SOC fixes D1 and D2 ship together. D1 alone makes spans of
20 years or less return a number, but still in t C per year, not kg CO2 (see D2).

### Fixed
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
- **D1:** a negative span (land-use year earlier than the baseline year) now raises
  `ValueError` instead of returning `None`.

### Added
- `tests/soc_test.py`: span tests (1 to 60 years), hand-calculated values, comparison
  with the previous loop for spans over 20 years, zero-area, zero-span and negative-span
  cases.

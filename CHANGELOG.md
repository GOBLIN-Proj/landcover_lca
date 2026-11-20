# Changelog

All notable changes to `landcover_lca` are recorded here, newest first. Format follows
[Keep a Changelog](https://keepachangelog.com/). Each SOC fix is tracked as a numbered
dossier (D1, D2, ...) in `artifacts/soc/` (local working folder, not in the repository).

## [Unreleased]

### Added
- **Example notebooks for the two packages that use landcover_lca** (replace `tests/example.py` and
  `tests/geo_example.py`). `tests/goblin_lite_example.ipynb`: the national tree, called as goblin_lite calls it (every
  total by land use and gas, baseline and scenarios, CO2e, drained grassland N2O reported in agriculture, horticultural
  peat already inside wetland CO2). `tests/geo_goblin_example.ipynb`: the geo tree, as geo_goblin calls it (the same
  totals, plus forest exports to water N, P and PO4e). Both note that `total_ch4_emission_cropland` and
  `total_n2o_emission_cropland` now take the same argument order as every other total (see the argument-order entry).
  `tests/examples_test.py` (in CI) runs both without Jupyter; the goblin_lite totals equal the national pins.

### Added
- **FIRE-3: forest fire CO2 switch, off by default (changes results).** `total_co2_emission_forest` and
  `total_co2_emission` (main and geo_goblin) take `include_fire_co2` (keyword only), **default False**: forest wildfire
  CO2 is no longer in the CO2 totals unless asked for. Reason: GOBLIN adds CBM forest carbon ("Total Ecosystem", the
  change in biomass, DOM and soil pools); cbm_runner simulates fire (DISTID3 = CBM default "Wildfire"), and CBM's
  disturbance matrices send the burnt carbon to the atmosphere (CBM-CFS3 v1.2 User's Guide s.1.8.5 p.15, Appendix 6,
  Table 8-1), so it was counted twice. The inventory counts it once (CRT 2026 Table4 4.A = 4.A stock change + 4(IV)
  wildfire CO2, exactly, 2020-2024). `include_fire_co2=True` restores it, to match the NID where no forest carbon model
  is added. CH4 and N2O from forest fire are not switched. goblin_lite national CO2: -18.55 kt in the baseline and
  scenarios (2020: 5,547.2 -> 5,528.7 kt). `burning_co2_forest` itself is unchanged.
  `tests/forest_fire_switch_test.py` (in CI).

### Changed
- **Rewetted CH4 basis checked (no result changes).** Grassland "rewet status" CH4 (68.1 / 216) is kg CH4-C, wetland
  rewetted CH4 (216) is kg CH4, as the NID applies them. New `TestRewettedCH4Basis` in `inventory_alignment_test`: the
  grassland split derived from the CRT CH4 reproduces the CRT on-site carbon only with the CH4-C reading (kg CH4 is
  3.5% low). Coverage row `grassland_organic_co2`: package/CRT exactly 1.0 since UNITS; tolerance 0.005 -> 0.001, stale
  note corrected.
- **EF3: factors no code reads (no result changes).** 8 removed from `emission_factors_land_use` (CSV and database):
  `share_forest_drainage_rich`/`_poor` (the split comes from the land-use input), `ef_co2_forest_share_harvested`/
  `_natural`, `ef_forest_Cf`, `ef_co2_forest_to_other_land`, `ef_co2_deforestation_biomass`/`_DOM` (forest carbon is
  CBM's). No package that uses landcover_lca reads them; they remain in git history. 6 unread factors are kept on
  purpose, each with the reason in its source cell (forest rewetting x3, cropland fire CO2 0, grassland mineral-soil
  fire CO2, the forest-to-grassland CRT reference). `units_test` now fails on any factor that no code reads and is
  not on that list.
- **EF1: sources for every database factor (no result changes).** `ef_co2_forest_to_settlement_mineral_soil` now
  cites NID 2026 s.6.3.6.2 p.239 (20% of 110 t C/ha over 20 years); `ef_co2_forest_to_settlement_drainage` is marked
  "not in NID 2026" (both only on the unreachable settlement path). The tables without a source column are documented in
  `docs/emission_factor_provenance.md`, "Other database tables" (NID Tables 6.21, 6.28, 6.31; SLAM nutrient export
  rates: doi 10.1007/s10666-020-09711-z). `land_use_features` "Grassland (unmanaged)" 0.95 -> 1.0, NID Table 6.31
  unimproved grassland (GR2); no calculation reads that row. `soc_inventory_test` expected failures 4 -> 3.
- **F6: forest drainage CO2 as the NID calculates it (changes results).** `Forest.co2_drainage_organic_soils_forest`
  (main and geo_goblin): CO2 (t C) = A_organic x (1.68 + 0.31) + A_organo-mineral x (1.68 x SD + 0.31).
  - No 50-year age cut-off: NID 2026 p.216 applies the factors "to all forest over the entire time series regardless
    of forest age". Before, forest over 50 years old (8.1%, table `national_forest_inventory_2017`) was removed from
    the CO2 area only; CH4 and N2O used the full area. `Forest.get_valid_area` and the `*_exclude_over_50` attributes
    are removed; CO2 now uses `forest_poor_drained_area` / `forest_rich_drained_area`, as CH4 and N2O.
  - Organo-mineral soil-depth factor SD = depth / 30 cm (NID eq 6.3.3-6.3.4): **0.581**, new factor
    `sd_forest_organo_mineral`, from NID Tables 6.7 and 6.15 (organo-mineral on-site / (area x 1.68), 4.A.1 + 4.A.2,
    2020-2023 = 381.0 kt C / (390.5 kha x 1.68) = 0.5808, 17.4 cm). Before, a depth of 28 cm (SD 0.933), hard-coded in
    `DataManager`. The NID text gives no depth.
  - The two old errors nearly cancelled (package/CRT 0.994-0.995); now 0.9998-1.0001 (2020-2023).
  - goblin_lite national: forest drainage CO2 1,628.9 -> 1,615.15 kt (-13.8 kt) in the baseline and both scenarios;
    national CO2 2020 5,561.0 -> 5,547.2 kt. Results move more where organo-mineral soil dominates (geo test data:
    -18.6 kt on 94.3 kt).
  - Derivation: `docs/emission_factor_provenance.md`, "Forest drainage CO2 (F6)". `tests/forest_drainage_co2_test.py`
    (in CI); inventory row `forest_drainage_co2` tolerance 0.01 -> 0.001.
- **D8: geo_goblin shares the national tree's mineral-soil SOC code (changes geo_goblin results for land converted to
  cropland or grassland).** `geo_goblin/land_classes/soc.py` re-exports `landcover_lca.land_classes.soc.SOC`, and
  `geo_lca_emissions` imports the mineral-soil CO2 and N2O functions (and `n2o_from_soil_carbon_loss`) from
  `lca_emission`, so the 0.3.0 SOC fixes now apply to geo_goblin and later fixes stay in step. Before, the geo copy
  returned `None` for spans of 20 years or less (D1), returned t C as kg CO2, about 3,667x too low (D2), raised a bare
  `KeyError` for a missing transition (D3), used SOCref 73.51 instead of LAC 85 t C/ha for cropland transitions (D4a),
  charged N2O from soil carbon loss as C x 1/15 only (D5) and did not check the years (D6). Example: 1,000 ha
  grassland to cropland over 30 years gave 1,102.65 ("kg CO2", in fact t C); it now gives 4,675,000 kg CO2.
  `mineral_soils_co2_grassland_remainging_grassland` (geo) renamed `mineral_soils_co2_grassland_remaining_grassland`,
  as in the national tree. geo test data totals unchanged (only grassland to forest, not in the totals).
  `tests/geo_soc_test.py` (in CI).
- **Argument order: `total_ch4_emission_cropland` and `total_n2o_emission_cropland` now take
  `(land_use_data, past_land_use_data, transition_matrix, ef_country)`, like every other total (main and geo_goblin).
  Callers must update.** They took `(ef_country, transition_matrix, land_use_data, past_land_use_data)`; a call in the
  old order raises `TypeError` naming the new order, so it cannot pass silently. Values unchanged.
  `tests/argument_order_test.py` (in CI) checks the order of every total in both trees. The scenario calls in
  `tests/goblin_lite_national_test.py` and `goblin_lite_n_test.py` also passed the baseline as current land use;
  corrected (no effect on the test data, where scenario cropland equals baseline cropland).
- **P1: off-site CO2 from horticultural peat in the national wetland total (changes results).**
  - **Callers: remove any separate `horticulture_co2_peat_export` addition**, or it is counted twice.
    `lca_emission.total_co2_emission_wetland` (and so `total_co2_emission`) now includes it, for the year carried by
    `land_use_data.wetland`, as the NID reports it in 4.D.1. goblin_lite gains it with no change (it never added it,
    although its docstring says wetland includes horticultural peat). The geo_goblin totals do not include it (national).
  - Tonnage = exports / 0.85 (NID 2026 s.6.6.3 p.279: 85% is exported, scaled up to include domestic use); new factor
    `frac_horticultural_peat_exported`. Before, exports alone were used (0.85x the CRT).
  - Exports for 2023 and 2024 added (UN Comtrade). Before, a calibration year after 2022 raised `KeyError`.
  - Years after the data use the mean of the last three years (2022-2024: 680.8 kt CO2), not the 2011-2022 mean
    (1,307.6 kt CO2 before). Years before the data raise `ValueError`. `calibration_year` is now optional and unused.
    The docstring gives the result in kg CO2 (it said metric tons).
  - The package reproduces the CRT 2026 4.D.1 wetland drainage CO2 exactly, 2020-2024 (was 0.884-0.900).
  - goblin_lite national CO2: baseline (2020) 3,776.4 -> 5,561.0 kt (+1,784.7); scenarios (2050) 4,689.2 -> 5,370.1
    kt and 4,692.4 -> 5,373.3 kt (+680.8).
  - Tests: `tests/peat_export_test.py` (new, in CI); the `wetland_drainage_co2` inventory row is now covered.
    `tests/example.py`, `output_test.py`, `goblin_lite_national_test.py` and `goblin_lite_n_test.py` no longer add it.
- **WET: wetland rewetted CH4 split by category; restored-wetland biomass removal fixed (changes results).**
  - Rewetted CH4: one factor per category, each on its own area (no rich/poor split is published). Industrial 216 kg
    CH4/ha (NID 2026 s.6.6.4.2, unchanged); domestic **106.4 kg CH4/ha**, the CRT 2026 4(II) "Other Domestic Peat
    Extraction" implied factor, a weighted average of the NID's 216 (rich) and 92 (poor), about 12% rich. Before, 216
    was applied to both. New column `ef_ch4_wetland_rewet_domestic`; misspelled columns renamed
    (`ef_ch4_wetland_rewet_off_site_deafult` -> `ef_ch4_wetland_rewet_industrial`,
    `ef_co2_wetland_rewet_off_site_deafult` -> `ef_co2_wetland_rewet_off_site_default`). An unknown factor name now
    raises a `KeyError` naming it.
  - `Wetland.co2_removals` (main and geo_goblin): the old loop divided by zero, misplaced brackets and called `len` on
    an int, so any non-zero `Wetland_to_Wetland` crashed. Now: removal in the target year = annual area x min(span, 5)
    x factor / 5 (NID s.6.6.4.1: 0.6 t C/ha/yr for 5 years to 3 t C/ha; same convention as D1). The CRT reports this
    gain as IE; 0 with the default GOBLIN inputs.
  - Docstrings: unmanaged wetland is area only (NID s.6.6.1); the `*_unmanaged_and_near_natural` methods use the
    near-natural area. geo_goblin applies the near-natural factors to all organic wetland (stated in its docstring).
  - Rewetted CO2 keeps the NID factors (0.5 / 0.24 t CO2-C/ha): rewetted domestic equals the CRT, rewetted industrial
    is 1.17-1.25x (the CRT mixes nutrient status). Industrial drained CH4 keeps the NID factors (the CRT implies
    22.6-23.6 kg CH4/ha against 32.9; documented). Rewetted CH4 216/92 is applied as kg CH4, as the NID does; the IPCC
    table gives kg CH4-C (documented in `docs/emission_factor_provenance.md`).
  - goblin_lite national CH4: baseline 142.0 -> 132.3 kt (-9.7, mostly because the 2020 input sets rewetted domestic
    = drained domestic, 88.3 kha; landcover_assignment); scenarios 126.0 -> 124.4 kt. CO2 and N2O unchanged.
  - Grassland fire CO2 switch: `include_fire_co2` renamed `include_peat_fire_co2` (main and geo_goblin) and now
    covers organic (peat) soil only, as the IPCC 2013 Wetlands Supplement (eq 2.8) asks. Mineral-soil fire CO2 is
    removed: neither the IPCC Tier 1 nor the NID counts it (the grass regrows). Default unchanged (0, as the NID).
    With the switch, goblin_lite baseline 7.5 kt (was 10.0 with mineral soil).
  - Tests: `tests/wetland_factors_test.py` (new, in CI). `inventory_alignment_test`: rewetted CH4 covered for
    domestic + industrial (0.98-1.03 per year); wetland fire, rewetted CO2 and industrial peat CH4 excluded with
    reasons; CRT "Other Domestic" mapped to rewetted domestic in `tests/inventory_inputs.py`.
- **UNITS: emission factors stored as published; conversions in one file (changes results).** The table
  `emission_factors_land_use` now holds each factor's published value and unit (e.g. 1.59 t CO2-C/ha/yr, 54.7 kg CH4-C,
  0.3 kg N2O-N) with its source. `resource_manager/units.py` holds the conversions (44/12, 16/12, 44/28, t to kg);
  `Emissions_Factors` (main and geo_goblin) converts on read, so callers receive the same units as before. New
  `Emissions_Factors.get_published_factor`. Readable copy of the table: `src/landcover_lca/database/emission_factors_land_use.csv`,
  written into the database by `tools/write_emission_factors.py` (`tools/derive_implied_forest_fire_factor.py --write`
  goes through it). `lca_emission.py` and `geo_lca_emissions.py` take their conversion constants from `units.py`.
  - Values that change: wetland fire Gef CO2 342 is g CO2-C per kg DM (CRT 4(IV) D.1 CO2/CH4 = 342 x 44/12 / 8.35 in
    every year), so wetland fire CO2 rises 3.67x; grassland organic-soil fire Gef 362 is g CO2-C (only used with
    `include_peat_fire_co2=True`); grassland and wetland drained-soil DOC 0.31 -> 0.3024 t C/ha/yr (IPCC 2013 eq 2.5, as
    the CRT implies, 1108.8 kg CO2/ha); forest DOC stays 0.31 t C (NID s.6.3 and Tables 6.7, 6.15 use 0.31); thirteen
    factors converted with 3.67 now use 44/12 (-0.09%).
  - goblin_lite national CO2: baseline 3,686.1 -> 3,776.4 kt (+90.3: wetland fire +102.9, other wetland -5.6, grassland
    -5.6, forest -1.5); scenarios +90.5 kt. CH4 and N2O unchanged.
  - Tests: `tests/units_test.py` (new, in CI): database equals the CSV, every unit is known, and every value the
    calculations receive is pinned against its previous value with each change listed. `n2o_drainage_factors_test` and
    `grassland_cropland_fire_test` check the published values; `soc_test` re-pinned.
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
- **FIRE-2: grassland fire CO2 is no longer counted (changes results).** NID 2026 s.6.5.4 (Tier 1) estimates grassland
  fire CH4 and N2O only, and the CRT reports CO2 as NO. `burning_co2_grassland` (main and geo_goblin) now returns 0
  unless `include_fire_co2=True`, which keeps the Table 6.34 calculation for later use. Resolves F4; F3 (362 g CO2 or
  CO2-C) only matters with that option.
  - goblin_lite national CO2: -4.50 kt baseline (3,690.6 -> 3,686.1 kt), -2.57 kt scenario 0, -2.56 kt scenario 1.
  - Grassland fire CH4/N2O unchanged. Documented difference from the NID: the burnt area is spread over soil types in
    proportion to their areas; the NID puts most of it on organic soil (unpublished split), so on inventory areas the
    package gives 0.57-0.72x the CRT. Cropland fire factors equal the NID; unchanged. README section "Fires".
  - Tests: `tests/grassland_cropland_fire_test.py` (new, in CI); `inventory_alignment_test` grassland fire CO2 covered,
    grassland and cropland fire CH4/N2O excluded with reasons; `soc_test` totals re-pinned.

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
  - Since then FIRE-1 and FIRE-2 have moved forest fire and grassland fire CO2 to covered, and grassland and cropland
    fire CH4/N2O to excluded (see Changed).

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

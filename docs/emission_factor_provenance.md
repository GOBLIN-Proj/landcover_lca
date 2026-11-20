# Provenance of the implied emission factors

An **implied** emission factor is worked back from reported inventory totals (kt CO2 divided by area). It is not a measured or default IPCC value. This page records, for each implied factor in the database
(`src/landcover_lca/database/landcover_lca_database.db`, table `emission_factors_land_use`), where it came from, how it was derived, and how to refresh it. The database also holds a `source` row and a `units` row under each factor (see **How factors are stored** below).

## How factors are stored (all factors)

**The database holds each factor as published**: the number printed in the NID, CRT or IPCC table, in that source's
unit, with the source cited. Nothing in the database has to be converted by hand to check it against its source.

- `src/landcover_lca/database/emission_factors_land_use.csv` is the readable copy of the table (the database is binary in
  git): one row per factor with `value`, `unit`, `source`. **To change a factor:** edit the CSV, run
  `tools/write_emission_factors.py`, run the tests. `tests/units_test.py` checks the database equals the CSV.
- `src/landcover_lca/resource_manager/units.py` holds every conversion (44/12, 16/12, 44/28, t to kg) and the list of
  units the table may use. `Emissions_Factors.get_emission_factor_in_emission_factor_data_base` converts on read, so the
  calculations receive kg CO2, kg CH4 or kg N2O per ha, g gas per kg dry matter, and so on.
  `Emissions_Factors.get_published_factor` returns the stored (value, unit).
- Carbon is converted with 44/12 exactly, as the inventory does (some values were previously converted with 3.67).

| published unit | calculations receive | conversion |
|---|---|---|
| t CO2-C/ha/yr, t C/ha | kg CO2/ha(/yr) | x 1000 x 44/12 |
| kg CH4-C/ha/yr | kg CH4/ha/yr | x 16/12 |
| kg N2O-N/ha/yr | kg N2O/ha/yr | x 44/28 |
| g CO2-C/kg dm | g CO2/kg dm | x 44/12 |
| t C/t air-dry peat | t CO2/t | x 44/12 |
| kg CH4/ha/yr, g CH4/kg dm, kg CO2/ha/yr (CRT-derived), t dm/ha, fraction, ... | same | none |

Values that changed when the table was moved to published units (UNITS):
- **Wetland fire Gef CO2 342 is g CO2-C per kg DM** (Wilson et al. 2015). The CRT shows this: 4(IV) D.1 CO2/CH4 = 150.18
  in every year = 342 x 44/12 / 8.35. It was read as g CO2, so wetland fire CO2 was 0.27x; now x 44/12 (= 1254 g CO2).
  The NID text writes "CO2 = 342 g kg-1".
- **Grassland organic-soil fire Gef CO2 362 is g CO2-C** (IPCC 2013 Wetlands Supplement Table 2.7; NID Table 6.34 prints
  g CO2). Grassland fire CO2 is off by default (FIRE-2), so this only matters with `include_peat_fire_co2=True`.
- **Drained-soil DOC differs by land use, as in the inventory.** Grassland and wetland: 0.31 -> **0.3024 t C/ha/yr**,
  IPCC 2013 eq 2.5 with the Table 2.2 temperate values, 0.21 x (1 + 0.60) x 0.9, as the CRT (implied 1108.8 kg CO2/ha for
  grassland and peat extraction; the NID text quotes 0.31). Forest: **0.31 t C/ha/yr, unchanged**, the IPCC Table 2.2
  value the NID states (s.6.3 p.216); NID Tables 6.7 and 6.15 reproduce it (DOC / drained area = 0.310 in 2020-2024).
- Rounding: thirteen factors had used 3.67 for 44/12 (-0.09%).
- **Difference from the IPCC, following the NID: grassland peat fire CO2.** IPCC 2013 Wetlands Supplement s.2.2.2.3:
  "it is good practice to report greenhouse gas emissions from fires on all managed lands with organic soils", CO2
  included (eq 2.8, Table 2.7: 362 g CO2-C per kg DM). The NID counts CH4 and N2O from grassland peat burnt (MB.Cf 336
  t DM/ha, Table 6.34) but no CO2 (s.6.5.4; CRT NO), while its wetland fire does count CO2 (s.6.6.5). The package
  burns grassland organic soil in proportion to its area and follows the NID: CO2 off by default.
  `include_peat_fire_co2=True` gives the organic-soil CO2 only. Mineral soil is never charged fire CO2 (neither the
  IPCC Tier 1 nor the NID counts it: the vegetation regrows), so `ef_wildfire_GEF_co2_mineral_soil_grassland` is not used.
- **Difference from the IPCC, following the NID: rewetted CH4 216 / 92.** IPCC 2013 Wetlands Supplement Table 3.3 gives
  these in kg CH4-C (temperate rich 216, poor 92). The NID applies them as kg CH4 for rewetted peat extraction ("216 kg
  CH4 and 92 kg CH4", s.6.6.4.2; CRT implied 208-221 kg CH4/ha confirms), so wetland is 12/16 = 0.75x the IPCC value.
  For rewetted grassland the NID applies them as kg CH4-C (68.1 / 216; the CRT 4(II) C.1 "other" row is reproduced
  with x 16/12). The package follows the NID in each case.

### Wetland rewetted CH4 (WET)

| Column | Published | Source |
|---|---|---|
| `ef_ch4_wetland_rewet_industrial` | 216 kg CH4/ha/yr | NID 2026 s.6.6.4.2 p.281, nutrient rich (IPCC 2013 WS Table 3.3), applied as kg CH4 as the NID does. CRT 4(II) rewetted industrial implied 208-221 by year |
| `ef_ch4_wetland_rewet_domestic` | 106.4 kg CH4/ha/yr | **CRT 2026 implied factor** (layer 3), 4(II) "Other Domestic Peat Extraction", constant 2020-2024: CH4 / area. Not stated in the NID. It is a weighted average of the NID's 216 (rich) and 92 (poor): (106.4 - 92) / (216 - 92) = 11.6% rich |

The inventory publishes no rich/poor split of the rewetted areas, so one factor is applied to each category, each to
its own area. "Other Domestic Peat Extraction" is the rewetted domestic area: its on-site (0.5 t C/ha) and DOC
(880 kg CO2/ha) implied factors equal the NID rewetted factors exactly. Checked by `tests/wetland_factors_test.py`.
Before WET a single 216 was applied to both areas (columns `ef_ch4_wetland_rewet_off_site_deafult` and
`ef_co2_wetland_rewet_off_site_deafult`, now `ef_ch4_wetland_rewet_industrial` and
`ef_co2_wetland_rewet_off_site_default`).

### Forest drainage CO2 (F6)

Method, NID 2026 s.6.3 (eq 6.3.2-6.3.4, p.215-216), as `Forest.co2_drainage_organic_soils_forest` (both trees):

    CO2 (t C/yr) = A_organic x (1.68 + 0.31) + A_organo-mineral x (1.68 x SD + 0.31),   kg CO2 = t C x 1000 x 44/12

| Item | Value | Source (layer) |
|---|---|---|
| A_organic, A_organo-mineral | area x `share_organic`, area x `share_organic_mineral` (drained N-poor, N-rich) | Input. The same areas as forest drainage CH4 and N2O. Should exclude open areas, as NID Tables 6.7 and 6.15 do (about 10%, not planted or drained; p.215) |
| Age cut-off | **none** | NID p.216: the factors "have been applied to all forest over the entire time series regardless of forest age" (layer 1, text) |
| `ef_co2_forest_drainage_on_site` | 1.68 t C/ha/yr | NID eq 6.3.2 (Jovani Sancho et al., 2021); Tables 6.7, 6.15: organic on-site / area = 1.68 every year |
| `ef_co2_forest_drainage_off_site_DOC` | 0.31 t C/ha/yr | NID p.216; Tables: DOC / area = 0.31 on both soils |
| `sd_forest_organo_mineral` | **0.581** (fraction) | NID eq 6.3.3-6.3.4, SD = depth / 30 cm. The text gives no depth; **the tables give SD** (layer 1, tables), below |

Derivation of SD from NID 2026 Table 6.7 (4.A.1, p.217) and Table 6.15 (4.A.2), organo-mineral on-site / (drained
organo-mineral area x 1.68):

| Category | Year | Area (kha) | On-site (kt C) | SD |
|---|---|---|---|---|
| 4.A.1 | 2020 | 63.5 | 61.5 | 0.5765 |
| 4.A.1 | 2021 | 66.2 | 64.2 | 0.5773 |
| 4.A.1 | 2022 | 68.3 | 66.3 | 0.5778 |
| 4.A.1 | 2023 | 69.7 | 67.6 | 0.5773 |
| 4.A.2 | 2020 | 33.9 | 33.5 | 0.5882 |
| 4.A.2 | 2021 | 31.3 | 30.9 | 0.5876 |
| 4.A.2 | 2022 | 29.5 | 29.2 | 0.5892 |
| 4.A.2 | 2023 | 28.1 | 27.8 | 0.5889 |
| **Pooled** | 2020-2023 | **390.5** | **381.0** | **0.5808** |

The package has one forest category, so the pooled value is used (0.577 in 4.A.1, 0.589 in 4.A.2; steady by year).
SD 0.581 is a soil depth of 17.4 cm. 2024 is left out: Table 6.7 prints 4.A.1 organo-mineral on-site as 0.0.

Check against the CRT 2026 (4.A organic-soil carbon, col T), on the NID drained areas, package/CRT:

| | 2020 | 2021 | 2022 | 2023 |
|---|---|---|---|---|
| Before F6: 50-year cut-off (x 0.919, CO2 only), depth 28 cm (SD 0.933) | 0.9951 | 0.9949 | 0.9950 | 0.9944 |
| Cut-off removed, SD 0.933 (calculated, not a package option) | 1.0830 | 1.0826 | 1.0825 | 1.0820 |
| **F6: no cut-off, SD 0.581** | **1.0001** | **0.9999** | **0.9999** | **0.9998** |

Before F6 the two errors nearly cancelled. Worked example: 1,000 ha organic and 500 ha organo-mineral give
1,000 x 1.99 + 500 x (1.68 x 0.581 + 0.31) = 1,990.0 + 643.04 = 2,633.04 t C = 9,654,480 kg CO2. Checked by
`tests/forest_drainage_co2_test.py` and the `forest_drainage_co2` row of `tests/inventory_alignment_test.py`
(tolerance 0.001). The depth constant 28 in `resource_manager/landcover_data_manager.py` and the age table
`national_forest_inventory_2017` are no longer used by the calculations.

### Horticultural peat, off-site CO2 (P1)

| Item | Value | Source |
|---|---|---|
| `frac_horticultural_peat_exported` | 0.85 (fraction) | NID 2026 s.6.6.3 p.279: "85 per cent of horticultural peat products are exported"; the export figures are scaled up to include domestic use. Tonnage used = exports / 0.85 |
| `ef_offsite_carbon_conversion_nutrient_poor` | 0.45 t C/t air-dry peat | IPCC 2006 Vol 4 Ch 7 Table 7.5 (nutrient poor), eq 7.5; NID 2026 s.6.6.4.2 p.280 |
| Table `UN_comtrade_exported_peat` | kg exported, 2011-2024 | UN Comtrade, HS 2703 (peat), reporter Ireland (372), partner world, flow export. The NID takes exports from the CSO via UN Comtrade / Eurostat. 2023 (348,444,751 kg) and 2024 (313,382,351 kg) added in P1, fetched 2026-11-19 from `comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=372&period=<year>&partnerCode=0&cmdCode=2703&flowCode=X` |

**CRT check (exact, 2020-2024).** CRT 2026 Table 4.D, industrial peat extraction, organic-soil carbon = 1.7 t C/ha x
4(II) industrial area + 0.45 x exports / 0.85. The exports this implies (919.4, 579.6, 390.4, 348.4, 313.4 kt) equal
the table. Comtrade has since revised 2021 (589.2 kt) and 2022 (401.6 kt); the table keeps the values the CRT 2026
used. Comtrade 2025 (370.7 kt) is beyond the CRT 2026 and not added. CO2 off-site: 2020 1,784.7 kt, 2024 608.3 kt.

**Years after the table** use the mean of its last three years (2022-2024: 350.7 kt exported, 680.8 kt CO2), so the
projection follows the data when a year is added. The NID gives no projection; the mean of the last three years was
chosen because exports fell from 919 kt in 2020 to 313 kt in 2024, and the 2011-2022 mean used before (792.5 kt)
reflects the earlier level of extraction. Years before the table raise ValueError.

**Totals.** National (main tree): in `total_co2_emission_wetland`, for the year carried by `land_use_data.wetland`.
geo_goblin: not included (a national export figure cannot be assigned to farms or catchments). Checked by
`tests/peat_export_test.py` and the `wetland_drainage_co2` row of `tests/inventory_alignment_test.py`.

**Source data for the two soil factors:** EPA CRT Table 4.C (Grassland), **2026 submission**, one workbook per year 1990-2024 (`IRL-CRT-2026-V1.0-<year>.xlsx`). The mineral-soil rows are extracted by `tools/extract_crt_table4c.py` into `tests/data/inventory/crt2026_4c_mineral_soils.csv` (and `crt2026_forest_conversions_mineral_soils.csv` for the cross-check below). The method is laid out step by step in the next section. CRT sign convention: + = gain of carbon, - = loss. The extract flips it to the package convention (+ emission, - removal): kg CO2/ha = -(t C/ha) x 1000 x 44/12. The 4.C.1 rows reproduce the NID 2026 key category table (+107.27 kt CO2 in 1990, -1,549.47 kt CO2 in 2024).

## Method, step by step (both soil factors)

1. **Get the data.** The EPA's 2026 CRT submission is one Excel workbook per inventory year, `IRL-CRT-2026-V1.0-<year>.xlsx`, 1990-2024. In this repository they are in `artifacts/data/national-inventory-2026/IRL-CRT-2026-V1.0/` (the folder is not committed to git; the zip is the EPA download).
2. **Find the rows.** In each workbook open sheet `Table4.C` (Grassland, "Sectoral background data"). The rows are found by their label, not by row number: `4.C.1. Grassland remaining grassland` and `4.C.2. Land converted to grassland` (in Ireland 4.C.2 is forest land only, row `4.C.2.a`).
3. **Read four cells from each row** (Excel columns): **D** total area (kha); **E** area of mineral soil (kha; for 4.C.2 the mineral area is the total area D, because the row has no organic soil); **K** implied net carbon stock change in mineral soils (t C per ha per year); **Q** net carbon stock change in mineral soils (kt C). These are the headings "Net carbon stock change in soils per area, Mineral soils" and "Carbon stock changes, Net carbon stock change in soils, Mineral soils".
4. **Change the sign.** The CRT reports + for a gain of carbon and - for a loss. The package reports + for an emission and - for a removal, so the sign is flipped. Convert carbon to CO2 with 44/12: `kt CO2 = -kt C x 44/12` and `kg CO2 per ha = -(t C per ha) x 1000 x 44/12`.
5. **Pool five years.** Take the latest five years, 2020-2024. Add the kt CO2 of the five years, add the mineral areas of the five years, and divide: `factor (kg CO2/ha/yr) = sum of kt CO2 / sum of area (kha) x 1000`. This weights each year by its area; it is not the average of the five yearly factors (for the grassland factor the two differ by less than 0.01 kg CO2/ha; for the forest factor they are identical because the CRT applies one constant rate).
6. **Store the result** in `src/landcover_lca/database/emission_factors_land_use.csv` (value, unit `kg CO2/ha/yr`, source), run `tools/write_emission_factors.py`, and record it on this page.
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
  fixtures in `tests/data/inventory/`; `--write` sets the value in `emission_factors_land_use.csv` and writes the table into the database). Test: `tests/forest_fire_factors_test.py`.
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

## Grassland and cropland fire factors (not implied; NID defaults)

| cells | values | source |
|---|---|---|
| `ef_wildfire_MB_time_CF_{mineral_soil,drained_organic_soil,wet_organic_soil}_grassland` | 4.1, 336, 66 t DM/ha | NID 2026 Table 6.34 |
| `ef_wildfire_GEF_ch4_*` grassland | 2.3, 9, 9 g/kg DM | NID 2026 Table 6.34 |
| `ef_wildfire_GEF_n2o_*` grassland | 0.21, 0.21, 0.21 g/kg DM | NID 2026 Table 6.34 |
| `ef_wildfire_GEF_co2_*` grassland | 1613 g CO2, 362, 362 g CO2-C per kg DM | NID 2026 Table 6.34 (362: IPCC 2013 WS Table 2.7, CO2-C); **not used by default** (FIRE-2) |
| `ef_wildfire_MB_time_CF_cropland`, `ef_ch4_cropland_Gef`, `ef_n2o_cropland_Gef` | 4.0 t DM/ha, 2.7, 0.07 g/kg DM | NID 2026 s.6.4.8 |

Checked by `tests/grassland_cropland_fire_test.py`. Grassland fire CO2 is 0 unless `include_peat_fire_co2=True` (organic soil only): NID 2026
s.6.5.4 (Tier 1) estimates CH4 and N2O only and the CRT reports CO2 as NO. 362 is stored as g CO2-C and converted
(x 44/12) if that option is used (F3).

**Soil split differs from the NID.** The package spreads the grassland burnt area over soil types in proportion to their
areas; the NID puts most of it on organic soil and does not publish the split (CRT CH4/N2O = 38.65 in every year, so about
87% of the dry matter burnt is organic). On inventory areas the package gives 0.57-0.72x the CRT CH4 and N2O. Cropland
matches the CRT where the burnt area is unrevised (2021); CRF 2024 areas for 2020 and 2022 were revised in the 2026 submission.

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

These factors are stored as published, in **kg N2O-N per ha per year**; the calculations receive kg N2O (x 44/28 = 1.5714, `units.py`). Checked by `tests/n2o_drainage_factors_test.py`.

| Column | Calculations receive (kg N2O) | Stored, published (kg N2O-N/ha/yr) | Source |
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

## Other database tables (no source column)

These tables have no `source` column, so their sources are recorded here (EF1). The SOC tables are checked against the
NID by `tests/soc_inventory_test.py`.

| Table | Values | Source | Check |
|---|---|---|---|
| `ipcc_soil_class_SOC` | Proportion / SOCref: HAC 0.01 / 95, LAC 0.71 / 85, Peaty/Humic 0.10 / 115, Sandy 0.01 / 71 t C/ha | NID 2026 Table 6.28 p.253 (IPCC 2006 Vol 4 Table 2.3 classes) | all match; the remaining 0.17 is wetland (organic), SOCref NA in the NID |
| `land_use_features` | cropland 0.69 (FLU), temporary grassland 0.82 (FLU), grassland and Grassland (managed) 1.14 (FI), Rough grazing 1.0, Other non agricultural land 1.0 | NID 2026 Table 6.31 p.262 (IPCC 2019 Refinement) | all match |
| `land_use_features` | Grassland (unmanaged) 1.0 | NID 2026 Table 6.31 p.262, unimproved grassland | was 0.95 (FMG 0.95), corrected in EF1; no calculation reads this row |
| `land_use_features` | forest 1.04 (FLU) | NID 2026 Table 6.21 p.239, Tier 2 average FLU for forest | matches |
| `national_forest_inventory_2017` | age classes | National Forest Inventory 2017 | not used by the calculations since F6 |
| `UN_comtrade_exported_peat` | kg exported, 2011-2024 | UN Comtrade HS 2703 | see "Horticultural peat, off-site CO2 (P1)" |
| `slam_nutrient_export_rates` | N and P kg/ha/yr by land cover (geo tree eutrophication only; not an inventory factor) | https://doi.org/10.1007/s10666-020-09711-z (reference supplied by the package owner) | the values have not been checked against the paper |

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
3. Update the value and source in `src/landcover_lca/database/emission_factors_land_use.csv` and run `tools/write_emission_factors.py`.
4. Update the numbers on this page, the constants in `tests/implied_factor_test.py`, `tests/soc_inventory_test.py` and the national totals in `tests/soc_test.py`, `CHANGELOG.md` and the emission-factor inventory.

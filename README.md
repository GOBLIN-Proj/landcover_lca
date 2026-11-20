# 🏘️🌳🌲🌽🍀 Land cover LCA for the GOBLIN model (Ireland only)

[![license](https://img.shields.io/badge/License-MIT-red)](https://github.com/GOBLIN-Proj/landcover_lca/blob/0.1.0/LICENSE)
[![python](https://img.shields.io/badge/python-3.9-blue?logo=python&logoColor=white)](https://github.com/GOBLIN-Proj/landcover_lca)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

 Based on the [GOBLIN](https://gmd.copernicus.org/articles/15/2239/2022/) (**G**eneral **O**verview for a **B**ackcasting approach of **L**ivestock **IN**tensification) land use tool module

 The package takes outputs from the landcover_assignment module (land use data and transition matrix) and produces emissions inventory for cropland, grassland, forest and wetlands 

 Currently parameterised for Ireland, the historic land uses and areas of organic and mineral soil are taken from the National Invetory [CRF Tables](https://www.epa.ie/publications/monitoring--assessment/climate-change/air-emissions/irelands-national-inventory-submissions-2022.php)

 Final result are pandas dataframes that can be read by numerous GOBLIN packages.

## Installation

Install from git hub. 

```bash
pip install "landcover_lca@git+https://github.com/GOBLIN-Proj/landcover_lca.git@main" 

```

Install from PyPI

```bash
pip install landcover_lca
```

## Usage
The baseline year represents the scenario baseline. The target year is the end year for each one of the scenarios. 

Transition dataframe is the land use transition matrix, and the land use dataframe is the areas for each land use. 

The land use dataframe includes proportions for area mineral, organic, rewetted, burnt, and peat extraction. 

Annual trade data has been used for horticultural peat exports. Off-site CO2 from horticultural peat is a national quantity: it is included in the national wetland total (`lca_emission.total_co2_emission_wetland`, used by goblin_lite) for the year the land-use data carries, and not in the geo_goblin totals.

```python
from landcover_lca.models import load_transition_matrix, load_land_use_data
import landcover_lca.lca_emission as lca
import pandas as pd
import os


def main():

    data_dir = "./data"

    ef_country = "ireland"
    baseline = 2020
    target = 2050

    transition = pd.read_csv(os.path.join(data_dir, "transition.csv"), index_col = 0)
    land_uses = pd.read_csv(os.path.join(data_dir, "land_uses.csv"), index_col = 0)

            
    transition_matrix = load_transition_matrix(transition, ef_country, baseline, target)
        
    land_use_data = load_land_use_data(land_uses, baseline)

    baseline_index = -1
    base = -baseline

    emission_df = pd.DataFrame(
        columns=["CO2", "CH4", "N2O", "CO2e"],
        index=pd.MultiIndex.from_product(
            [
                # list(scenario_list),
                [baseline_index],
                ["cropland", "grassland", "forest", "wetland", "total"],
                [
                    baseline
                ],
            ],
            names=["scenario", "land_use", "year"],
        ),
    )

    emission_df.index.levels[0].astype(int)

    emission_df.loc[
            (
                baseline_index,
                "total",
                baseline,
            ),
            "CH4",
        ] = (
            lca.total_ch4_emission(
                land_use_data[base],
                land_use_data[base],
                transition_matrix[base],
                ef_country
            )

        )
    emission_df.loc[
            (
                baseline_index,
                "total",
                baseline,
            ),
            "CO2",
        ] = lca.total_co2_emission(
            land_use_data[base],
            land_use_data[base],
            transition_matrix[base],
            ef_country
        ) 

    emission_df.loc[
            (
                baseline_index,
                "total",
                baseline,
            ),
            "N2O",
        ] = (
            lca.total_n2o_emission(
                land_use_data[base],
                land_use_data[base],
                transition_matrix[base],
                ef_country
            )
        )
    
    emission_df.loc[
            (
                baseline_index,
                "cropland",
                baseline
            ),
            "CO2",
        ] = lca.total_co2_emission_cropland(
            land_use_data[base],
            land_use_data[base],
            transition_matrix[base],
            ef_country
        )

    emission_df.loc[
            (
                baseline_index,
                "cropland",
                baseline,
            ),
            "CH4",
        ] = lca.total_ch4_emission_cropland(
            land_use_data[base],
            land_use_data[base],
            transition_matrix[base],
            ef_country,
                
    
            )
    
    emission_df.loc[
            (
                baseline_index,
                "cropland",
                baseline,
            ),
            "N2O",
        ] = (
            lca.total_n2o_emission_cropland(
                land_use_data[base],
                land_use_data[base],
                transition_matrix[base],
                ef_country,
            )
        )
    
    
    emission_df.loc[
            (
                baseline_index,
                "grassland",
                baseline,
            ),
            "CO2",
        ] = (
            lca.total_co2_emission_grassland(
                land_use_data[base],
                land_use_data[base],
                transition_matrix[base],
                ef_country
            )
        )
    
    emission_df.loc[
            (
                baseline_index,
                "grassland",
                baseline,
            ),
            "CH4",
        ] = (
            lca.total_ch4_emission_grassland(
                land_use_data[base],
                land_use_data[base],
                transition_matrix[base],
                ef_country
            )
            
        )
    
    emission_df.loc[
            (
                baseline_index,
                "grassland",
                baseline
            ),
            "N2O",
        ] = (
            lca.total_n2o_emission_grassland(
                land_use_data[base],
                land_use_data[base],
                transition_matrix[base],
                ef_country
            )
        )
    emission_df.loc[
            (
                baseline_index,
                "wetland",
                baseline,
            ),
            "CO2",
        ] = (
            lca.total_co2_emission_wetland(
                land_use_data[base],
                land_use_data[base],
                transition_matrix[base],
                ef_country,
            )  # includes off-site CO2 from horticultural peat for the baseline year
        )
    emission_df.loc[
            (
                baseline_index,
                "wetland",
                baseline,
            ),
            "CH4",
        ] = (
            lca.total_ch4_emission_wetland(
                land_use_data[base],
                land_use_data[base],
                transition_matrix[base],
                ef_country
            )
        )
    emission_df.loc[
            (
                baseline_index,
                "wetland",
                baseline,
            ),
            "N2O",
        ] = (
            lca.total_n2o_emission_wetland(
                land_use_data[base],
                land_use_data[base],
                transition_matrix[base],
                ef_country,
            )
        )
    emission_df.loc[
            (
                baseline_index,
                "forest",
                baseline,
            ),
            "CO2",
        ] = (
            lca.total_co2_emission_forest(
                land_use_data[base],
                land_use_data[base],
                transition_matrix[base],
                ef_country,

            )
            
        ) 
    emission_df.loc[
            (
                baseline_index,
                "forest",
                baseline
            ),
            "CH4",
        ] = (
            lca.total_ch4_emission_forest(
                land_use_data[base],
                land_use_data[base],
                transition_matrix[base],
                ef_country
            )
           
        )
    emission_df.loc[
            (
                baseline_index,
                "forest",
                baseline
            ),
            "N2O",
        ] = (
            lca.total_n2o_emission_forest(
                land_use_data[base],
                land_use_data[base],
                transition_matrix[base],
                ef_country
            )

        )

    emission_df["CO2e"] = (
            emission_df["CO2"]
            + (emission_df["CH4"] * 28)
            + (emission_df["N2O"] * 295)
        )
    print(emission_df)

if __name__ == "__main__":
    main()

    
```
## Soil organic carbon (mineral soils): method, units and assumptions

Mineral-soil carbon change from land-use change follows the Irish National Inventory Document (NID 2026), equation 6.4.3 (IPCC Tier 1, equation 2.25):

```
C = A x (SOC_past - SOC_current) / T          T = 20 years
SOC = SOCref x adjustment factor              (FLU x FMG x FI, NID Table 6.31)
```

Implemented in `land_classes/soc.py` and called by the `mineral_soils_co2_from_<past>_to_<current>` functions in `lca_emission.py`.

**Units.** Every CO2 total returned by this package is in **kg CO2**, positive for an emission and negative for a removal (goblin_lite multiplies by 1e-6 to report kt). The `SOC` class itself returns **t C per year**; the `lca_emission` functions convert it (x 1000 x 44/12).

**What one call returns.** An annual emission rate at one evaluated year (`year_range` = evaluated year minus baseline year, read by `models.get_time_period` from the year of the destination land use in the two datasets), not a time series. Converted area is assumed to convert in equal annual slices, each releasing `delta SOC / 20` per year for 20 years, so `min(year_range, 20)` slices contribute. For spans of 20 years or less the timing of conversion does not matter; for longer spans the equal-slice assumption does. The span is validated (D6): a missing destination category raises a `KeyError` naming the dataset, and a source category carrying a different year from the destination in the same dataset raises a `ValueError`.

**Assumptions to be aware of**

| Assumption | Detail | Inventory |
|---|---|---|
| **All grassland is "improved" grassland** | Every conversion to or from grassland uses the database row `grassland`, adjustment factor **1.14**. There is no improved / unimproved / rough-grazing split. A grassland-to-cropland conversion is therefore assumed to start from the highest-carbon grassland (1.14 against cropland 0.69). | NID Table 6.31 gives improved 1.14, unimproved 1.0, temporary 0.82, rough grazing 1.0. The adjustment factors for these exist in the database but are not selected. |
| SOCref: LAC 85 for cropland transitions, otherwise a weighted mean of four soil classes | Any transition involving cropland uses LAC, **85 t C/ha** (NID s.6.4.6; reproduces Table 6.32). Other transitions use the weighted mean, 73.51 t C/ha. The class proportions (HAC 0.01, LAC 0.71, peaty 0.10, sandy 0.01) sum to 0.83 because organic soils (0.17) have no SOCref, and they are not renormalised. | For forest to grassland the inventory uses Tier 2 soil-group values (planned, D4b). Converted grassland stays improved grassland (1.14) for cropland conversions too: scenario conversions are permanent, unlike the temporary-grassland rotation in Table 6.32. |
| Forest uses adjustment factor 1.04 | Tier 2 average from NID Table 6.21. | Forest to grassland is a **known simplification, not changed**. The package mixes Tier 1 SOCref 73.51 with the Tier 2 forest factor 1.04 and the Tier 1 grassland 1.14: -7.35 t C/ha over 20 years, **a removal**. The inventory (CRT 2026, 4.C.2) reports **an emission**: a constant loss of 0.896 t C/ha/yr, 17.9 t C/ha over 20 years (+3,285.34 kg CO2/ha/yr, stored unused as `ef_co2_implied_forest_to_grassland_SOC_per_ha`). The signs differ. landcover_assignment never creates forest transitions, so GOBLIN never reaches this path; grassland to forest (afforestation) is the transition that occurs, and CBM covers forests. |
| Grassland remaining grassland is one constant | `ef_co2_implied_grassland_remaining_SOC_per_ha`, -371.985 kg CO2/ha/yr, a single implied value. | The inventory series runs from about +27 (1990) to about -400 kg CO2/ha/yr (2023). |
| N2O from soil carbon loss (forest to grassland) | Follows NID eq 11.8 and 11.10: N mineralised = soil C lost / 15; direct N2O-N = N x EF1 (0.006); indirect N2O-N = N x FracLEACH (0.1) x EF5 (0.011); N2O = N2O-N x 44/28. Result in kg N2O per year, 11.16 times the previous value. | Reproduces CRT Table 4(III) row 4(III).C.2.a for every year (`tests/soc_n2o_test.py`). Constants are in `lca_emission.py` and documented in `docs/emission_factor_provenance.md`. The sign follows the soil carbon: the Tier 1 forest to grassland gives a gain of carbon (D4b), so the N2O is negative here; the inventory has a loss and a positive N2O. |

The inventory reports **no land converted to cropland** (CRT 4.B.2 is NO), so there is no inventory total for conversions to cropland. The nearest inventory values are the rotation table (NID Table 6.32) and the grassland-remaining-grassland series; both are used in `tests/soc_inventory_test.py`. Known gaps against the inventory are recorded there as expected failures.

**Which conversion terms are in use.** All of these are available and aligned with the inventory as far as the table says. Several are **not yet used by GOBLIN scenarios**, because landcover_assignment writes only `Grassland_to_<X>` columns and the national scenarios do not yet change cropland area. They are kept, tested and documented so the capacity is there when a scenario needs them; a term that is not in the totals is a choice, not a defect.

| Transition | Function | In the totals? | Can landcover_assignment supply it? | Inventory counterpart | What it currently represents |
|---|---|---|---|---|---|
| Grassland to cropland | `mineral_soils_co2_from_grassland_to_cropland` | CO2: yes | Yes (the only conversion into cropland it can write). Area is 0 in current scenarios; cropland change is planned | None: CRT 4.B.2 is NO. Checked per hectare against NID Table 6.32 | SOCref LAC 85 (D4a). Assumes improved grassland (1.14). No N2O from the soil carbon loss: the NID reports it under Agriculture (3.D.1.5, C:N 10) |
| Forest to cropland | `mineral_soils_co2_from_forest_to_cropland` | CO2: yes | No (no `Forest_to_*` columns) | NID: no such transitions detected | Tier 1, LAC 85 |
| Cropland to grassland | `mineral_soils_co2_from_cropland_to_grassland` | CO2: yes | No | NID: no permanent transition found in the rotation analysis | Tier 1, LAC 85 |
| Forest to grassland | `mineral_soils_co2_from_forest_to_grassland`, `mineral_soils_n2o_from_forest_to_grassland` | CO2 and N2O: yes | No | CRT 4.C.2: an emission, 0.896 t C/ha/yr | Tier 1 gives the opposite sign (D4b, expected-failure test). The N2O chain matches the CRT (D5). The inventory rate is stored, unused, as `ef_co2_implied_forest_to_grassland_SOC_per_ha` |
| Grassland to forest, cropland to forest | `mineral_soils_co2_from_grassland_to_forest`, `..._cropland_to_forest` | **No**: CBM covers forest soils | Grassland to forest: yes (afforestation) | Forest soils are in the CBM runs | Callable directly; not summed in any total |
| Grassland remaining grassland | `mineral_soils_co2_grassland_remaining_grassland` | CO2: yes, every year | Not a transition: uses the mineral grassland area | CRT 4.C.1, Tier 1 | Implied factor, -392.73 kg CO2/ha/yr (D7). The only soil carbon term that is non-zero in the goblin_lite national case |

**Converted land is assumed to be mineral soil, for land leaving grassland.** The area that leaves grassland for another use (rewetting excepted) is charged the mineral-soil carbon change in full. Its exact soil type is not known and no mineral share is applied, so the result does not depend on the soil shares in the land use data (`tests/soc_test.py`, `TestConvertedAreaIsAssumedMineral`). NID 2026 s.6.4.6 makes the same assumption for cropland. In GOBLIN scenarios the land converted is grassland on mineral soil, moving to another use. Drained organic grassland that is rewetted is not a conversion: it is a change in the grassland's soil shares, charged by the `Grassland` rewetting terms, not by this code. **The assumption does not hold for land moving into grassland** (forest to grassland, cropland to grassland): those hectares may be organic soil and would be charged both the mineral-soil change and, as part of the current grassland area, the drained-organic terms (`land_classes/grassland.py`), a double count. No mineral share is applied there either; these transitions are not yet used by GOBLIN scenarios.

**Required transition-matrix columns.** The SOC and land use code read 8 of the matrix columns: `Grassland_to_Grassland`, `Cropland_to_Cropland`, `Forest_to_Forest`, `Wetland_to_Wetland`, `Grassland_to_Cropland`, `Forest_to_Cropland`, `Cropland_to_Grassland` and `Forest_to_Grassland`. If one is missing, a `KeyError` names it and lists the columns present. A missing column is never treated as zero.

Implied emission factors (values derived from inventory totals) are documented in `docs/emission_factor_provenance.md`: source table, submission, years, formula and how to refresh them. The tables without a `source` column (soil classes, adjustment factors, forest age classes, peat exports, SLAM nutrient export rates) have their sources in the same file, section "Other database tables".

**geo_goblin uses the same code (D8).** The geo tree has no SOC copy of its own: `geo_goblin/land_classes/soc.py` re-exports the SOC class above, and `geo_lca_emissions` imports the mineral-soil CO2 and N2O functions from `lca_emission`. So every fix in this section applies to geo_goblin too. Grassland remaining grassland stays in the geo tree (it reads the geo land-use columns) and uses the same method and factor.

## Cropland change: what the package assumes

Scenarios can convert grassland to cropland. `landcover_assignment` supplies the area; this package
charges the mineral-soil carbon change (NID 2026 eq 6.4.3, see the section above). Checked end to end by
`tests/cropland_readiness_test.py`: 100,000 ha of grassland to cropland over 30 years gives 467.5 kt CO2/yr
(SOC term, kg CO2 in the code).

**What `landcover_assignment` provides (the contract)**
- Cropland can only grow. A scenario sets a cropland share of the spared area; future cropland area is current plus allocated.
- The converted land is mineral grassland. It is written as `Grassland_to_Cropland` (ha over the whole period). Only `Grassland_to_<X>` columns are ever written: cropland to grassland, forest to anything and so on are always 0.
- The transition code writes `abs(change in area)`, which loses direction. It is harmless while cropland only grows. Any fix is in `landcover_assignment`, not here (logged there as a later item).

**Assumptions in this package**
- **New cropland is mineral soil**, so there is no drainage term for organic cropland. Existing cropland is 100% mineral in the data. A term would be needed only if cropland could gain organic soil.
- **Improved grassland (GR1).** All converted grassland is treated as improved (adjustment factor 1.14, NID Table 6.31); cropland is 0.69; SOCref is LAC 85 t C/ha. This is the higher-emission case. If a share u of the converted area were unimproved (factor 1.0), the emission would fall by u x 0.14/0.45: 3.1% per 10% unimproved, 31% if all of it. The unimproved, temporary (0.82) and rough/other (1.0) factors are already in the database but are not used, because the improved/unimproved split of the converted area is not supplied. If it were supplied, the cost of converting each grassland type could be computed; this is a planned extension.
- **The cropland factor is a crop-phase value.** The inventory's cropland includes temporary grassland in rotation (factor 0.82). A scenario hectare is taken as permanently under crops (0.69), which is the higher-emission case. A temporary-grass share could be added later in the same way as the grassland partition.

**What the inventory does, and what is not modelled (CR1, NI1)**
- The inventory reports **no conversion to cropland** (CRT 4.B.2 = NO; NID 2026 s.6.4). The method here (IPCC Tier 1, eq 6.4.3, NID factors) reproduces the NID's Table 6.32 rotation values, but there is no inventory total for converted land to compare against.
- **Cropland remaining cropland (CRT 4.B.1) is not modelled.** The NID defines cropland as crops plus temporary grassland in crop rotations (a fixed cohort of 133,929 LPIS parcels, 9,909 rotation patterns). Each parcel's soil carbon falls under crops (0.69) and recovers under temporary grass (0.82). The CRT figure is the net of those movements in a year, so it is not a sink from annual cropping: it is +27.7, +22.0, +17.6, -28.3, -9.0 kt C for 2020-2024 (removal in 2020-22, emission in 2023-24; five-year mean about -22 kt CO2/yr, 0.6% of the goblin_lite baseline). It follows the share of land in the grass phase, so a fixed factor would be misleading. Documented, not modelled.

## Fires: what the package charges, and where it differs from the NID

Area burnt = land-use area x `share_burnt` (from the input). Emissions = area burnt x factor (IPCC eq 2.27).

| Land use | CO2 | CH4, N2O | Same as the NID? |
|---|---|---|---|
| Forest | yes | yes | Yes. Factors per ha burnt are the 2020-2022 inventory values (FIRE-1). `share_burnt` must be the total forest burnt area. |
| Grassland | **0 by default** | yes | CO2: yes, the NID (Tier 1) does not count it. CH4/N2O: same factors, **different soil split** (below). |
| Cropland | none | yes | Yes (NID s.6.4.8 factors). |

**Forest fire CO2: off by default, because CBM already counts it.** `total_co2_emission_forest` and `total_co2_emission` take `include_fire_co2` (keyword only, both trees), **default False**. GOBLIN (goblin_lite, geo_goblin, forest_sim) adds the CBM forest carbon ("Total Ecosystem", the change in biomass, dead organic matter and soil pools) to landcover_lca's forest CO2. cbm_runner simulates fire (`DISTID3` = CBM default "Wildfire"), and CBM's disturbance matrices send the burnt carbon to the atmosphere (CBM-CFS3 v1.2 User's Guide s.1.8.5 p.15, Appendix 6), so that loss is already in the CBM change. The inventory counts it once: CRT 2026 Table4 4.A = 4.A carbon stock change + 4(IV) wildfire CO2, exactly, every year 2020-2024. Pass `include_fire_co2=True` when no forest carbon model is added, to match the NID (CRT 4(IV).A): goblin_lite baseline 18.55 kt CO2. Fire CH4 and N2O are always included (GOBLIN takes only carbon from CBM).

**Grassland CO2.** Not required under the NID: s.6.5.4 estimates CH4 and N2O only, and the CRT reports CO2 as NO. CO2 from fires on grassland peat (organic soil), which the IPCC 2013 Wetlands Supplement asks for (eq 2.8), is available as `burning_co2_grassland(..., include_peat_fire_co2=True)` (7.5 kt in the goblin_lite baseline). It is never added to the totals. Mineral soil is never charged fire CO2: burnt grass regrows, and neither the IPCC Tier 1 nor the NID counts it.

**Grassland soil split (differs from the NID).** Both use NID Table 6.34 for mineral, drained organic and undrained organic soil. The package spreads the burnt area over the soil types in proportion to their areas (about 8% organic). The NID puts most of it on organic soil (half of peatland fires are counted as rough grazing; about 87% of the dry matter burnt is organic) and does not publish the split. On the inventory's own areas the package gives 0.57-0.72x the CRT grassland CH4 and N2O. This is deliberate: it needs no unpublished split, and fire emissions still respond to drainage and rewetting.

## Wetlands: where the package differs from the NID

Peat extraction (domestic and industrial), rewetted peat and near-natural wetland use the NID 2026 s.6.6 factors. On the inventory's own areas, domestic peat extraction and near-natural wetland reproduce the CRT exactly.

| Item | Package | NID / CRT |
|---|---|---|
| Rewetted CH4 | One factor per category. Industrial 216 kg CH4/ha (NID, applied as kg CH4 as the NID does; the IPCC table gives kg CH4-C). Domestic **106.4 kg CH4/ha** | The NID gives 216 (nutrient rich) and 92 (poor) and publishes no area split. 106.4 is the CRT's implied factor for rewetted domestic ("Other Domestic Peat Extraction"), a weighted average of the two (about 12% rich). Package/CRT 0.98-1.03 |
| Rewetted CO2 | NID factors, 0.5 t CO2-C/ha on-site and 0.24 off-site | Domestic equals the CRT. Industrial is 1.17-1.25x the CRT, which mixes nutrient status (not published) |
| Industrial drained CH4 | 32.9 kg CH4/ha, as domestic (NID) | CRT implied 22.6-23.6 on the same area. The NID factor is used and the difference documented |
| Unmanaged wetland | Area only | As the NID (s.6.6.1). Near-natural wetland carries the removals and CH4 |
| Restored-wetland biomass (`Wetland_to_Wetland`) | 0.6 t C/ha/yr for 5 years after restoration (NID s.6.6.4.1), D1 convention | The CRT reports this as IE. 0 with the default GOBLIN inputs |
| Fire | NID factors; CO2 Gef 342 is g CO2-C | The factors match the CRT ratios; the burnt-area basis differs (see Fires) |
| Horticultural peat, off-site CO2 | Exports / 0.85 x 0.45 t C/t x 44/12 (NID s.6.6.3-6.6.4.2), in the national wetland total. Exports 2011-2024 (UN Comtrade); later years use the mean of the last three years (680.8 kt CO2) | As the NID; the CRT 4.D.1 industrial row is reproduced exactly 2020-2024. The NID gives no projection. Not in the geo_goblin totals (national figure) |

## Forest drainage CO2: how it is calculated

As NID 2026 s.6.3 (eq 6.3.2-6.3.4): `CO2 (t C) = A_organic x (1.68 + 0.31) + A_organo-mineral x (1.68 x 0.581 + 0.31)`, then x 1000 x 44/12 for kg CO2. A is the drained forest area on each soil (`share_organic`, `share_organic_mineral`), the same area as forest drainage CH4 and N2O, and should exclude open areas (roads, extraction routes), as the NID does. No age cut-off: the NID applies the factors to all forest regardless of age. 0.581 is the organo-mineral soil-depth factor (depth / 30 cm); the NID text gives no depth, so it is taken from NID Tables 6.7 and 6.15 (on-site / (area x 1.68), 2020-2023: 0.5808, 17.4 cm). This reproduces the CRT 2026 4.A organic-soil carbon (package/CRT 0.9998-1.0001, 2020-2023). Derivation in `docs/emission_factor_provenance.md`, section "Forest drainage CO2 (F6)".

## Emission factors: stored as published

The database table `emission_factors_land_use` holds each factor **as published**: the number and unit printed in the NID, CRT or IPCC table, with its source. A value can be checked against its source without any arithmetic. All unit conversions (44/12, 16/12, 44/28, t to kg) are in one file, `src/landcover_lca/resource_manager/units.py`, and are applied when a factor is read, so the calculations receive kg CO2, kg CH4 or kg N2O per ha (or g per kg dry matter for fires).

- Readable copy of the table: `src/landcover_lca/database/emission_factors_land_use.csv` (value, unit, source per factor). The database is binary in git, so this file is where changes are reviewed.
- To change a factor: edit the CSV, run `python tools/write_emission_factors.py`, run the tests (`tests/units_test.py` checks the database equals the CSV).
- Details and the list of values that changed when this was introduced: `docs/emission_factor_provenance.md`, "How factors are stored".

## Inventory alignment (tests)

`tests/inventory_alignment_test.py` gives the package the national inventory's own areas (NID/CRT 2026) and compares each emission term with the CRT 2026 emissions, for 2020-2024 (fire: 2020-2022, the only years with a published burnt area). The package itself is not changed or calibrated by these tests.

- Inputs: `tests/data/inventory/` holds CRT 2026 cells (`crt2026_lulucf.csv`), CRF 2024 burnt areas (`crf2024_burnt_area.csv`) and NID 2026 forest drained areas (`nid2026_forest_organic_soils.csv`). Every value records its source cell or table. The two CSVs from workbooks are rebuilt by `tools/extract_inventory_fixtures.py` (needs `openpyxl`, in the Poetry dev group).
- `tests/inventory_inputs.py` builds the land-use table and transition matrix. Its docstring states how each inventory row maps to a package share and the caveats.
- `tests/data/inventory/inventory_coverage.csv` lists every comparison as **covered** (must match within its tolerance), **gap** (a known difference owned by a fix; run as an expected failure) or **excluded** (out of scope, with the reason). Every term in `total_{co2,ch4,n2o}_emission` and every CRT Table4 category is in the map.

Current state: forest drainage CO2/CH4/N2O, grassland remaining mineral CO2, grassland organic CO2, peat extraction N2O, near-natural CH4 and wetland rewetted CH4 (domestic and industrial) match. The grassland CH4 rows are only a consistency check (the rich/poor split is derived from them). Forest fire CO2/CH4/N2O match since FIRE-1, and grassland fire CO2 (0, as the NID) since FIRE-2. Excluded, with the reason in the map: grassland and cropland fire CH4/N2O (soil split and area basis), wetland fire (area basis), rewetted wetland CO2 and industrial peat CH4 (see Wetlands). Wetland drainage CO2, including off-site CO2 from horticultural peat, matches exactly since P1. No known gaps remain in the map.

## License
This project is licensed under the terms of the MIT license.

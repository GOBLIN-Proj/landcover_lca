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

Annual trade data has been used for horticultural peat exports.

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
            ef_country,
            transition_matrix[base],
            land_use_data[base],
            land_use_data[base]
                
    
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
                ef_country,
                transition_matrix[base],
                land_use_data[base],
                land_use_data[base],
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
            ) + lca.horticulture_co2_peat_export(ef_country, baseline, baseline)
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

Implied emission factors (values derived from inventory totals) are documented in `docs/emission_factor_provenance.md`: source table, submission, years, formula and how to refresh them.

Not yet updated for these fixes: the parallel `geo_goblin` copy.

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

## License
This project is licensed under the terms of the MIT license.

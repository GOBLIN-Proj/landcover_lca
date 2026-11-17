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

**What one call returns.** An annual emission rate at one evaluated year (`year_range` = evaluated year minus baseline year), not a time series. Converted area is assumed to convert in equal annual slices, each releasing `delta SOC / 20` per year for 20 years, so `min(year_range, 20)` slices contribute. For spans of 20 years or less the timing of conversion does not matter; for longer spans the equal-slice assumption does.

**Assumptions to be aware of**

| Assumption | Detail | Inventory |
|---|---|---|
| **All grassland is "improved" grassland** | Every conversion to or from grassland uses the database row `grassland`, adjustment factor **1.14**. There is no improved / unimproved / rough-grazing split. A grassland-to-cropland conversion is therefore assumed to start from the highest-carbon grassland (1.14 against cropland 0.69). | NID Table 6.31 gives improved 1.14, unimproved 1.0, temporary 0.82, rough grazing 1.0. The adjustment factors for these exist in the database but are not selected. |
| SOCref: LAC 85 for cropland transitions, otherwise a weighted mean of four soil classes | Any transition involving cropland uses LAC, **85 t C/ha** (NID s.6.4.6; reproduces Table 6.32). Other transitions use the weighted mean, 73.51 t C/ha. The class proportions (HAC 0.01, LAC 0.71, peaty 0.10, sandy 0.01) sum to 0.83 because organic soils (0.17) have no SOCref, and they are not renormalised. | For forest to grassland the inventory uses Tier 2 soil-group values (planned, D4b). Converted grassland stays improved grassland (1.14) for cropland conversions too: scenario conversions are permanent, unlike the temporary-grassland rotation in Table 6.32. |
| Forest uses adjustment factor 1.04 | Tier 2 average from NID Table 6.21. | Forest to grassland is a **known simplification, not changed**. The package mixes Tier 1 SOCref 73.51 with the Tier 2 forest factor 1.04 and the Tier 1 grassland 1.14 (-7.35 t C/ha, a removal). The NID uses Tier 2 soil-group values (Tables 6.20, 6.21; s.6.3.6.2): about -1.0 t C/ha to improved grassland using the average factors, and it depends strongly on soil group. landcover_assignment never creates forest transitions, so GOBLIN never reaches this path; grassland to forest (afforestation) is the transition that occurs, and CBM covers forests. |
| Grassland remaining grassland is one constant | `ef_co2_implied_grassland_remaining_SOC_per_ha`, -371.985 kg CO2/ha/yr, a single implied value. | The inventory series runs from about +27 (1990) to about -400 kg CO2/ha/yr (2023). |
| N2O from soil carbon loss is incomplete | Only `delta C x 1/15` (forest to grassland), without the emission factor, 44/28 or indirect N2O. | NID eq 11.8. |

The inventory reports **no land converted to cropland** (CRT 4.B.2 is NO), so there is no inventory total for conversions to cropland. The nearest inventory values are the rotation table (NID Table 6.32) and the grassland-remaining-grassland series; both are used in `tests/soc_inventory_test.py`. Known gaps against the inventory are recorded there as expected failures.

**Required transition-matrix columns.** The SOC and land use code read 8 of the matrix columns: `Grassland_to_Grassland`, `Cropland_to_Cropland`, `Forest_to_Forest`, `Wetland_to_Wetland`, `Grassland_to_Cropland`, `Forest_to_Cropland`, `Cropland_to_Grassland` and `Forest_to_Grassland`. If one is missing, a `KeyError` names it and lists the columns present. A missing column is never treated as zero.

Implied emission factors (values derived from inventory totals) are documented in `docs/emission_factor_provenance.md`: source table, submission, years, formula and how to refresh them.

Not yet updated for these fixes: the parallel `geo_goblin` copy.

## License
This project is licensed under the terms of the MIT license.

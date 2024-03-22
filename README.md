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

When prompted enter your ```<username>``` and password, which is your ```<access_token>```.

```<access_token>``` is provided by the repo manager.

```<username>``` pass your own github username.


```bash
pip install "landcover_lca@git+https://github.com/GOBLIN-Proj/landcover_lca.git@main" 

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
## License
This project is licensed under the terms of the MIT license.

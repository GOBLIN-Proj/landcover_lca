# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 10:22:52 2023

@author: Colm Duffy
"""

import numpy as np
import pandas as pd

from landcover_lca.land_utils import (
    SOC,
    Wetland,
    Grassland,
    Cropland,
    Forest,
)

from landcover_lca.models import Emissions_Factors, Land_Use_Features
from landcover_lca.data_loader import Loader


# scalar vars
t_to_kg = 1e3
kt_to_kg = 1e6
C_to_N = 1.0 / 15.0
kha_to_ha = 1e3


###################################################################################################################
#############  FOREST ###########################
#################################################

# Organic soils
# Drainage
def co2_drainage_organic_soils_forest(
    ef_country, transition_matrix, land_use_data, past_land_use_data
):
    """Proportion drained, if older than 50 years, not emitting"""

    FOREST = Forest(
        ef_country,
        transition_matrix,
        land_use_data,
        past_land_use_data,
        "forest",
        "forest",
    )

    return FOREST.co2_drainage_organic_soils_forest()


def ch4_drainage_organic_soils_forest(
    ef_country, transition_matrix, land_use_data, past_land_use_data
):

    FOREST = Forest(
        ef_country,
        transition_matrix,
        land_use_data,
        past_land_use_data,
        "forest",
        "forest",
    )

    return FOREST.ch4_drainage_organic_soils_forest()


def n2o_drainage_organic_soils_forest(
    ef_country, transition_matrix, land_use_data, past_land_use_data
):

    FOREST = Forest(
        ef_country,
        transition_matrix,
        land_use_data,
        past_land_use_data,
        "forest",
        "forest",
    )

    return FOREST.n2o_drainage_organic_soils_forest()


# Rewetting Forest soils
# National Inventory Report: Forest soils are managed to maintain drains so that nutrient uptake and crop productivity is
# maintained. Therefore, forest soils are not rewetted.


# Total organic soils
def organic_soils_co2_forest(
    ef_country, transition_matrix, land_use_data, past_land_use_data
):
    return co2_drainage_organic_soils_forest(
        ef_country, transition_matrix, land_use_data, past_land_use_data
    )


def organic_soils_ch4_forest(
    ef_country, transition_matrix, land_use_data, past_land_use_data
):
    return ch4_drainage_organic_soils_forest(
        ef_country, transition_matrix, land_use_data, past_land_use_data
    )


# Mineral soils
def mineral_soils_co2_from_cropland_to_forest(
    land_use,
    past_land_use_data,
    transition_matrix_data,
    ef_country
):
    soc = SOC(
        ef_country,
        land_use,
        past_land_use_data,
        transition_matrix_data,
        "cropland",
        "forest",
    )

    return soc.compute_emissions_from_mineral_soils_in_land_use_change()


def mineral_soils_co2_from_grassland_to_forest(
    land_use,
    past_land_use_data,
    transition_matrix_data,
    ef_country
):

    soc = SOC(
        ef_country,
        land_use,
        past_land_use_data,
        transition_matrix_data,
        "grassland",
        "forest",
    )

    return soc.compute_emissions_from_mineral_soils_in_land_use_change()


def mineral_soils_co2_to_forest(
    land_use,
    past_land_use_data,
    transition_matrix_data,
    ef_country,
):
    return mineral_soils_co2_from_cropland_to_forest(
        land_use,
        past_land_use_data,
        transition_matrix_data,
        ef_country,
    ) + mineral_soils_co2_from_grassland_to_forest(
        land_use,
        past_land_use_data,
        transition_matrix_data,
        ef_country,
    )


# Burning
def burning_co2_forest(
    ef_country, transition_matrix, land_use_data, past_land_use_data
):

    FOREST = Forest(
        ef_country,
        transition_matrix,
        land_use_data,
        past_land_use_data,
        "forest",
        "forest",
    )

    return FOREST.burning_co2_forest() * t_to_kg


def burning_ch4_forest(
    ef_country, transition_matrix, land_use_data, past_land_use_data
):

    FOREST = Forest(
        ef_country,
        transition_matrix,
        land_use_data,
        past_land_use_data,
        "forest",
        "forest",
    )

    return FOREST.burning_ch4_forest() * t_to_kg


def burning_n2o_forest(
    ef_country, transition_matrix, land_use_data, past_land_use_data
):

    FOREST = Forest(
        ef_country,
        transition_matrix,
        land_use_data,
        past_land_use_data,
        "forest",
        "forest",
    )

    return FOREST.burning_n2o_forest() * t_to_kg


# Total
def total_co2_emission_forest(
    land_use_data,
    past_land_use_data,
    transition_matrix,
    ef_country,
):
    return (
        burning_co2_forest(
            ef_country, transition_matrix, land_use_data, past_land_use_data
        )
        + organic_soils_co2_forest(
            ef_country, transition_matrix, land_use_data, past_land_use_data
        )
        - mineral_soils_co2_to_forest(
            land_use_data,
            past_land_use_data,
            transition_matrix,
            ef_country,
        )
    )


def total_ch4_emission_forest(
    land_use_data, past_land_use_data, transition_matrix, ef_country
):
    return organic_soils_ch4_forest(
        ef_country, transition_matrix, land_use_data, past_land_use_data
    ) + burning_ch4_forest(
        ef_country, transition_matrix, land_use_data, past_land_use_data
    )


def total_n2o_emission_forest(
    land_use_data, past_land_use_data, transition_matrix, ef_country
):
    return burning_n2o_forest(
        ef_country, transition_matrix, land_use_data, past_land_use_data
    ) + n2o_drainage_organic_soils_forest(
        ef_country, transition_matrix, land_use_data, past_land_use_data
    )


# Assume no deforestation for conversion to other lands

#################################################
#############  GRASSLAND ########################
#################################################

# Organic soils
# Drainage
def drainage_co2_organic_soils_in_grassland(
    land_use, past_land_use_data, transition_matrix, ef_country
):

    GRASSLAND = Grassland(
        ef_country,
        transition_matrix,
        land_use,
        past_land_use_data,
        "grassland",
        "grassland",
    )

    return GRASSLAND.drainage_co2_organic_soils_in_grassland()


def drainage_ch4_organic_soils_in_grassland(
    land_use, past_land_use_data, transition_matrix, ef_country
):

    GRASSLAND = Grassland(
        ef_country,
        transition_matrix,
        land_use,
        past_land_use_data,
        "grassland",
        "grassland",
    )

    return GRASSLAND.drainage_ch4_organic_soils_in_grassland()


def drainage_n2O_organic_soils_in_grassland(
    land_use, past_land_use_data, transition_matrix, ef_country
):

    GRASSLAND = Grassland(
        ef_country,
        transition_matrix,
        land_use,
        past_land_use_data,
        "grassland",
        "grassland",
    )

    return GRASSLAND.drainage_n2O_organic_soils_in_grassland()


# Rewetting
def rewetting_co2_organic_soils_in_grassland(
    land_use, past_land_use_data, transition_matrix, ef_country
):

    GRASSLAND = Grassland(
        ef_country,
        transition_matrix,
        land_use,
        past_land_use_data,
        "grassland",
        "wetland",
    )

    return GRASSLAND.rewetting_co2_organic_soils_in_grassland()


def rewetting_ch4_organic_soils_in_grassland(
    land_use, past_land_use_data, transition_matrix, ef_country
):

    GRASSLAND = Grassland(
        ef_country,
        transition_matrix,
        land_use,
        past_land_use_data,
        "grassland",
        "wetland",
    )

    return GRASSLAND.rewetting_ch4_organic_soils_in_grassland()


# Mineral soils
def mineral_soils_co2_from_forest_to_grassland(
    land_use,
    past_land_use_data,
    transition_matrix_data,
    ef_country,
):
    soc = SOC(
        ef_country,
        land_use,
        past_land_use_data,
        transition_matrix_data,
        "forest",
        "grassland",
    )
    return soc.compute_emissions_from_mineral_soils_in_land_use_change()


def mineral_soils_co2_from_cropland_to_grassland(
    land_use,
    past_land_use_data,
    transition_matrix_data,
    ef_country,
):

    soc = SOC(
        ef_country,
        land_use,
        past_land_use_data,
        transition_matrix_data,
        "cropland",
        "grassland",
    )

    return soc.compute_emissions_from_mineral_soils_in_land_use_change()


def mineral_soils_n2o_from_forest_to_grassland(
    land_use,
    past_land_use_data,
    transition_matrix_data,
    ef_country,
):

    soc = SOC(
        ef_country,
        land_use,
        past_land_use_data,
        transition_matrix_data,
        "forest",
        "grassland",
    )

    emissions_from_mineralization = (
        soc.compute_emissions_from_mineral_soils_in_land_use_change() * C_to_N
    )

    return emissions_from_mineralization


# Burning
def burning_co2_grassland(
    ef_country, transition_matrix, land_use, past_land_use_data
):

    GRASSLAND = Grassland(
        ef_country,
        transition_matrix,
        land_use,
        past_land_use_data,
        "grassland",
        "grassland",
    )

    return GRASSLAND.burning_co2_grassland() * t_to_kg


def burning_ch4_grassland(
    ef_country, transition_matrix, land_use, past_land_use_data
):

    GRASSLAND = Grassland(
        ef_country,
        transition_matrix,
        land_use,
        past_land_use_data,
        "grassland",
        "grassland",
    )

    return GRASSLAND.burning_ch4_grassland() * t_to_kg


def burning_n2o_grassland(
    ef_country, transition_matrix, land_use, past_land_use_data
):

    GRASSLAND = Grassland(
        ef_country,
        transition_matrix,
        land_use,
        past_land_use_data,
        "grassland",
        "grassland",
    )

    return GRASSLAND.burning_n2o_grassland() * t_to_kg


# total emissions
def total_co2_emission_to_grassland(
    land_use,
    past_land_use_data,
    transition_matrix,
    ef_country,
):
    return mineral_soils_co2_from_forest_to_grassland(
        land_use,
        past_land_use_data,
        transition_matrix,
        ef_country,
    ) + mineral_soils_co2_from_cropland_to_grassland(
        land_use,
        past_land_use_data,
        transition_matrix,
        ef_country,
    )


def total_co2_emission_in_grassland(
    land_use, past_land_use_data, transition_matrix, ef_country
):
    return drainage_co2_organic_soils_in_grassland(
        land_use, past_land_use_data, transition_matrix, ef_country
    ) + rewetting_co2_organic_soils_in_grassland(
        land_use, past_land_use_data, transition_matrix, ef_country
    )


def total_ch4_emission_in_grassland(
    land_use,
    past_land_use_data,
    transition_matrix,
    ef_country,
):
    return drainage_ch4_organic_soils_in_grassland(
        land_use, past_land_use_data, transition_matrix, ef_country
    ) + rewetting_ch4_organic_soils_in_grassland(
        land_use, past_land_use_data, transition_matrix, ef_country
    )


def total_co2_emission_grassland(
    land_use,
    past_land_use_data,
    transition_matrix,
    ef_country,
):
    return (
        total_co2_emission_to_grassland(
            land_use,
            past_land_use_data,
            transition_matrix,
            ef_country
        )
        + total_co2_emission_in_grassland(
            land_use, past_land_use_data, transition_matrix, ef_country
        )
        + burning_co2_grassland(
            ef_country, transition_matrix, land_use, past_land_use_data
        )
    )


def total_ch4_emission_grassland(
    land_use,
    past_land_use_data,
    transition_matrix,
    ef_country,
):
    return total_ch4_emission_in_grassland(
        land_use,
        past_land_use_data,
        transition_matrix,
        ef_country,
    ) + burning_ch4_grassland(
        ef_country, transition_matrix, land_use, past_land_use_data
    )


def total_n2o_emission_grassland(
    land_use,
    past_land_use_data,
    transition_matrix,
    ef_country,
):
    return (
        burning_n2o_grassland(
            ef_country, transition_matrix, land_use, past_land_use_data
        )
        + mineral_soils_n2o_from_forest_to_grassland(
            land_use,
            past_land_use_data,
            transition_matrix,
            ef_country,
        ))
                #+ drainage_n2O_organic_soils_in_grassland(
            #land_use, past_land_use_data, transition_matrix, ef_country
       # )
    


###############################################
#############  WETLAND ########################
###############################################

# Peat extraction
def horticulture_co2_peat_export(ef_country, year, calibration_year):

    data_loader_class = Loader(ef_country)
    emissions_factors = Emissions_Factors(ef_country)
    ef_offsite_carbon_conversion_nutrient_poor = (
        emissions_factors.get_emission_factor_in_emission_factor_data_base(
            "ef_offsite_carbon_conversion_nutrient_poor"
        )
    )

    past_export_peat_df = data_loader_class.exported_peat()

    past_export_peat_df.fillna(0, inplace=True)

    if year <= calibration_year:
        export_weight = past_export_peat_df.loc[year, "Total_kg"]
    else:
        export_weight = past_export_peat_df["Total_kg"].mean()

    return (export_weight * ef_offsite_carbon_conversion_nutrient_poor) * (44 / 12)


# Organic soils
# Biomass
def biomass_co2_wetland_to_peatland(
    land_use_data, past_land_use_data, transition_matrix, ef_country
):

    WETLAND = Wetland(
        ef_country,
        transition_matrix,
        land_use_data,
        past_land_use_data,
        "wetland",
        "wetland",
    )

    return WETLAND.co2_removals()


# Drainage
def drainage_co2_organic_soils_in_wetland(
    land_use_data, past_land_use_data, transition_matrix, ef_country
):

    WETLAND = Wetland(
        ef_country,
        transition_matrix,
        land_use_data,
        past_land_use_data,
        "wetland",
        "wetland",
    )

    return WETLAND.co2_emissions_wetland_drained()


def drainage_ch4_organic_soils_in_wetland(
    ef_country, transition_matrix, land_use_data, past_land_use_data
):
    WETLAND = Wetland(
        ef_country,
        transition_matrix,
        land_use_data,
        past_land_use_data,
        "wetland",
        "wetland",
    )

    return WETLAND.drainage_ch4_organic_soils()


def drainage_n2o_organic_soils_in_wetland(
    ef_country, transition_matrix, land_use_data, past_land_use_data
):

    WETLAND = Wetland(
        ef_country,
        transition_matrix,
        land_use_data,
        past_land_use_data,
        "wetland",
        "wetland",
    )

    return WETLAND.drainage_n2o_organic_soils()


# Burning
def burning_co2_wetland(
    ef_country, transition_matrix, land_use_data, past_land_use_data
):
    WETLAND = Wetland(
        ef_country,
        transition_matrix,
        land_use_data,
        past_land_use_data,
        "wetland",
        "wetland",
    )

    return WETLAND.burning_co2_wetland() * t_to_kg


def burning_ch4_wetland(
    ef_country, transition_matrix, land_use_data, past_land_use_data
):
    WETLAND = Wetland(
        ef_country,
        transition_matrix,
        land_use_data,
        past_land_use_data,
        "wetland",
        "wetland",
    )

    return WETLAND.burning_ch4_wetland() * t_to_kg


def burning_n2o_wetland(
    ef_country, transition_matrix, land_use_data, past_land_use_data
):
    WETLAND = Wetland(
        ef_country,
        transition_matrix,
        land_use_data,
        past_land_use_data,
        "wetland",
        "wetland",
    )

    return WETLAND.burning_n2o_wetland() * t_to_kg


# Total
def total_co2_emission_wetland(
    land_use_data, past_land_use_data, transition_matrix, ef_country
):
    return (
        drainage_co2_organic_soils_in_wetland(
            land_use_data, past_land_use_data, transition_matrix, ef_country
        )
        + biomass_co2_wetland_to_peatland(
            land_use_data, past_land_use_data, transition_matrix, ef_country
        )
        + burning_co2_wetland(
            ef_country, transition_matrix, land_use_data, past_land_use_data
        )
    )


def total_ch4_emission_wetland(
    land_use_data, past_land_use_data, transition_matrix, ef_country
):
    return drainage_ch4_organic_soils_in_wetland(
        ef_country, transition_matrix, land_use_data, past_land_use_data
    ) + burning_ch4_wetland(
        ef_country, transition_matrix, land_use_data, past_land_use_data
    )


def total_n2o_emission_wetland(
    land_use_data, past_land_use_data, transition_matrix, ef_country
):
    return drainage_n2o_organic_soils_in_wetland(
        ef_country, transition_matrix, land_use_data, past_land_use_data
    ) + burning_n2o_wetland(
        ef_country, transition_matrix, land_use_data, past_land_use_data
    )


###################################################################################################################
#############  CROPLAND ########################
#################################################

# mineral soil
def mineral_soils_co2_from_forest_to_cropland(
    land_use_data,
    past_land_use_data,
    transition_matrix,
    ef_country,
):

    soc = SOC(
        ef_country,
        land_use_data,
        past_land_use_data,
        transition_matrix,
        "forest",
        "cropland",
    )

    return soc.compute_emissions_from_mineral_soils_in_land_use_change()


def mineral_soils_co2_from_grassland_to_cropland(
    land_use_data,
    past_land_use_data,
    transition_matrix,
    ef_country,
):

    soc = SOC(
        ef_country,
        land_use_data,
        past_land_use_data,
        transition_matrix,
        "grassland",
        "cropland",
    )

    return soc.compute_emissions_from_mineral_soils_in_land_use_change()


# Burning

# Emissions factor of zero for Co2 burning, IPCC 2006 Table 2.5, notes that the emissions for co2 assumed to be in balance


def burning_ch4_cropland(
    ef_country, transition_matrix, land_use_data, past_land_use_data
):

    CROPLAND = Cropland(
        ef_country,
        transition_matrix,
        land_use_data,
        past_land_use_data,
        "cropland",
        "cropland",
    )

    return CROPLAND.burning_ch4_cropland() * t_to_kg


def burning_n2o_cropland(
    ef_country, transition_matrix, land_use_data, past_land_use_data
):

    CROPLAND = Cropland(
        ef_country,
        transition_matrix,
        land_use_data,
        past_land_use_data,
        "cropland",
        "cropland",
    )

    return CROPLAND.burning_n2o_cropland() * t_to_kg


# Total
def total_co2_emission_cropland(
    land_use_data,
    past_land_use_data,
    transition_matrix_data,
    ef_country
):

    result = mineral_soils_co2_from_forest_to_cropland(
        land_use_data,
        past_land_use_data,
        transition_matrix_data,
        ef_country
    ) + mineral_soils_co2_from_grassland_to_cropland(
        land_use_data,
        past_land_use_data,
        transition_matrix_data,
        ef_country
    )
    return result


def total_ch4_emission_cropland(
    ef_country, transition_matrix, land_use_data, past_land_use_data
):
    return burning_ch4_cropland(
        ef_country, transition_matrix, land_use_data, past_land_use_data
    )


def total_n2o_emission_cropland(
    ef_country, transition_matrix, land_use_data, past_land_use_data
):
    return burning_n2o_cropland(
        ef_country, transition_matrix, land_use_data, past_land_use_data
    )


###################################################################################################################
#############  SETTLEMENT #######################
#################################################

# Organic soils
def drainage_co2_organic_soils_in_settlement(land_use, ef_country):
    """
    Here we overestimate drainage emissions because we use forest as a reference for previous land_use of organic soil converted to settlement.

    ef_co2_forest_to_settlement_drainage include onsite and offite emissions

    """
    ef_co2_forest_to_settlement_drainage = (
        ef_country.get_emission_factor_in_emission_factor_data_base(
            "ef_co2_forest_to_settlement_drainage"
        )
    )
    return (
        ef_co2_forest_to_settlement_drainage
        * land_use.settlement.area_ha
        * land_use.settlement.share_drained_in_organic
        * land_use.settlement.share_organic
    )


def drainage_ch4_organic_soils_in_settlement(land_use, ef_country):
    """
    Here we underestimate drainage emissions because we use forest as a reference for previous land_use of organic soil converted to settlement.

    """
    ef_ch4_forest_drainage_land = (
        ef_country.get_emission_factor_in_emission_factor_data_base(
            "ef_ch4_forest_drainage_land"
        )
    )
    ef_ch4_forest_drainage_ditch = (
        ef_country.get_emission_factor_in_emission_factor_data_base(
            "ef_ch4_forest_drainage_ditch"
        )
    )

    frac_ditch = ef_country.get_emission_factor_in_emission_factor_data_base(
        "frac_ditch"
    )

    return (
        (
            ef_ch4_forest_drainage_land * (1.0 - frac_ditch)
            + ef_ch4_forest_drainage_ditch * frac_ditch
        )
        * land_use.settlement.area_ha
        * land_use.settlement.share_drained_in_organic
        * land_use.settlement.share_organic
    )


# Mineral soils
def mineral_soils_co2_from_forest_to_settlement(land_use, ef_country):
    ef_co2_forest_to_settlement_mineral_soil = (
        ef_country.get_emission_factor_in_emission_factor_data_base(
            "ef_co2_forest_to_settlement_mineral_soil"
        )
    )
    return (
        ef_co2_forest_to_settlement_mineral_soil
        * land_use.settlement.area_ha
        * land_use.settlement.share_mineral_soil
        * land_use.settlement.share_from_forest
    )


# Total
def total_co2_settlement(land_use, ef_country):
    """
    No change in biomass. Change only in SOC of mineral soil and drainage from organic soils.

    Parameters
    ----------
    land_use : Land_use object
        include area, information about water management for each land_use
    ef_country : dataframe
        Emission factor data base

    Returns
    -------
    float
        Change of SOC from forest to settlement

    """
    return mineral_soils_co2_from_forest_to_settlement(
        land_use, ef_country
    ) + drainage_co2_organic_soils_in_settlement(land_use, ef_country)


def total_ch4_settlement(land_use, ef_country):
    return drainage_ch4_organic_soils_in_settlement(land_use, ef_country)


###################################################################################################################
#############  TOTAL ############################
#################################################


def total_co2_emission(
    land_use_data,
    past_land_use_data,
    transition_matrix_data,
    ef_country,
):

    return (
        total_co2_emission_cropland(
            land_use_data,
            past_land_use_data,
            transition_matrix_data,
            ef_country
        )
        + total_co2_emission_wetland(
            land_use_data, past_land_use_data, transition_matrix_data, ef_country
        )
        + total_co2_emission_forest(
            land_use_data,
            past_land_use_data,
            transition_matrix_data,
            ef_country,
        )
        + total_co2_emission_grassland(
            land_use_data,
            past_land_use_data,
            transition_matrix_data,
            ef_country,
        )
    )


def total_ch4_emission(
    land_use_data,
    past_land_use_data,
    transition_matrix,
    ef_country,
):
    return (
        total_ch4_emission_wetland(
            land_use_data, past_land_use_data, transition_matrix, ef_country
        )
        + total_ch4_emission_grassland(
            land_use_data,
            past_land_use_data,
            transition_matrix,
            ef_country
        )
                + total_ch4_emission_cropland(
            ef_country, transition_matrix, land_use_data, past_land_use_data
        ) 
        + total_ch4_emission_forest(
            land_use_data, past_land_use_data, transition_matrix, ef_country
        )

    )


def total_n2o_emission(
    land_use_data,
    past_land_use_data,
    transition_matrix,
    ef_country,
):
    return (
        total_n2o_emission_wetland(
            land_use_data, past_land_use_data, transition_matrix, ef_country
        )
        + total_n2o_emission_grassland(
            land_use_data,
            past_land_use_data,
            transition_matrix,
            ef_country,
        )
        + total_n2o_emission_forest(
            land_use_data, past_land_use_data, transition_matrix, ef_country
        )
        + total_n2o_emission_cropland(
            ef_country, transition_matrix, land_use_data, past_land_use_data
        )
    )

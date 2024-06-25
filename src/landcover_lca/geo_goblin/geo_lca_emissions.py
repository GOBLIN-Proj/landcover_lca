# -*- coding: utf-8 -*-
"""
Description:
    Calculates emissions from land cover change. It imports various modules and classes related to 
    land use and emissions factors. The script defines functions to estimate carbon dioxide (CO2) and methane (CH4) Nitrous Oxide (N2O) emissions from land cover change.
    from the various land cover types.

    These functions take into account current/future and historical land use data, emission factor country, and transition matrices. 

Note: 
    This is part of a larger suite of tools developed for environmental data analysis and modeling. 
"""

import numpy as np
import pandas as pd

from landcover_lca.geo_goblin.land_classes.soc import SOC
from landcover_lca.geo_goblin.land_classes.wetland import Wetland
from landcover_lca.geo_goblin.land_classes.grassland import Grassland
from landcover_lca.geo_goblin.land_classes.cropland import Cropland
from landcover_lca.geo_goblin.land_classes.forestland import Forest
from landcover_lca.geo_goblin.geo_models import Emissions_Factors, Land_Use_Features
from landcover_lca.resource_manager.data_loader import Loader


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
    """
    Estimates carbon dioxide (CO2) emissions from the drainage of organic soils in forest areas,
    based on current and historical land use data. This function utilizes the Forest class to
    calculate the emissions, with a focus on areas that have been drained and are not older than
    50 years, as it is assumed these older areas do not emit CO2 due to drainage.

    Parameters:
        - ef_country (string): Emission factor country.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.



    Returns:
        float: The estimated CO2 emissions resulting from the drainage of organic soils in
               forest areas. This estimation is based on current and historical land use data,
               and it excludes emissions from forest areas older than 50 years.

    Note:
        The function initializes an instance of the Forest class, passing in relevant data,
        and invokes its `co2_drainage_organic_soils_forest` method to perform the emissions
        calculation.
    """

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
    """
    Calculate the CH4 emissions from drainage of organic soils in forest land.

    Parameters:
        - ef_country (string): Emission factor country.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.



    Returns:
        float: The calculated CH4 emissions from drainage of organic soils in forest land.
    """

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
    """
    Calculate the N2O emissions from drainage of organic soils in forest land use.

    Parameters:
        - ef_country (string): Emission factor country.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.



    Returns:
        float: N2O emissions from drainage of organic soils in forest land use.
    """

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
    """
    Calculate CO2 emissions from organic soils in a forest.

    Parameters:
        - ef_country (string): Emission factor country.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.


    Returns:
    float: CO2 emissions from organic soils in the forest.
    """
    return co2_drainage_organic_soils_forest(
        ef_country, transition_matrix, land_use_data, past_land_use_data
    )


def organic_soils_ch4_forest(
    ef_country, transition_matrix, land_use_data, past_land_use_data
):
    """
    Calculate CH4 emissions from organic soils in forest land use.

    Parameters:
        - ef_country (string): Emission factor country.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.



    Returns:
    float: CH4 emissions from organic soils in forest land use.
    """
    return ch4_drainage_organic_soils_forest(
        ef_country, transition_matrix, land_use_data, past_land_use_data
    )


# Mineral soils
def mineral_soils_co2_from_cropland_to_forest(
    land_use, past_land_use_data, transition_matrix_data, ef_country
):
    """
    Calculates the CO2 emissions from mineral soils during the transition from cropland to forest.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.


    Returns:
    float: The computed CO2 emissions from mineral soils in the land use change.
    """

    soc = SOC(
        ef_country,
        land_use,
        past_land_use_data,
        transition_matrix_data,
        "forest",
        "cropland",
    )

    return soc.compute_emissions_from_mineral_soils_in_land_use_change()


def mineral_soils_co2_from_grassland_to_forest(
    land_use, past_land_use_data, transition_matrix_data, ef_country
):
    """
    Calculate CO2 emissions from mineral soils during land use change from grassland to forest.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.


    Returns:
    float: The calculated CO2 emissions from mineral soils during land use change.
    """

    soc = SOC(
        ef_country,
        land_use,
        past_land_use_data,
        transition_matrix_data,
        "forest",
        "grassland",
    )

    return soc.compute_emissions_from_mineral_soils_in_land_use_change()


def mineral_soils_co2_to_forest(
    land_use,
    past_land_use_data,
    transition_matrix_data,
    ef_country,
):
    """
    Calculates the CO2 from mineral soils to forest land use.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.



    Returns:
        float: CO2 from mineral soils to forest land use.
    """

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
    """
    Calculate the CO2 emissions from burning forests.

    Parameters:
        - ef_country (string): Emission factor country.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.


    Returns:
        float: CO2 emissions from burning forests.
    """
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
    """
    Calculate the CH4 emissions from burning forests.

    Parameters:
        - ef_country (string): Emission factor country.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.


    Returns:
    float: The CH4 emissions from burning forests.
    """

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
    """
    Calculate the N2O emissions from burning forests.

    Parameters:
        - ef_country (string): Emission factor country.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.

    Returns:
        float: N2O emissions from burning forests.
    """

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
    """
    Calculate the total CO2 emission from forest land use change.

    Mineral soils are not included here as they are accounted for in the CBM model.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.

    Returns:
        float: Total CO2 emission from forest land use change.
    """
    return burning_co2_forest(
        ef_country, transition_matrix, land_use_data, past_land_use_data
    ) + organic_soils_co2_forest(
        ef_country, transition_matrix, land_use_data, past_land_use_data
    )


def total_ch4_emission_forest(
    land_use_data, past_land_use_data, transition_matrix, ef_country
):
    """
    Calculate the total CH4 emission from forest based on land use data, past land use data,
    transition matrix, and emission factor for the country.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.

    Returns:
    float: Total CH4 emission from forest.
    """

    return organic_soils_ch4_forest(
        ef_country, transition_matrix, land_use_data, past_land_use_data
    ) + burning_ch4_forest(
        ef_country, transition_matrix, land_use_data, past_land_use_data
    )


def total_n2o_emission_forest(
    land_use_data, past_land_use_data, transition_matrix, ef_country
):
    """
    Calculate the total N2O emission from forest land use.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.

    Returns:
        float: Total N2O emission from forest land use.
    """
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

def drainage_co2_organic_soils_in_grassland(
    land_use, past_land_use_data, transition_matrix, ef_country
):
    """
    Calculate the CO2 emissions from drainage of organic soils in grassland.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.



    Returns:
    - The CO2 emissions from drainage of organic soils in grassland.
    """

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
    """
    Calculate the CH4 emissions from organic soils in grassland due to drainage.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.

    Returns:
    - The calculated CH4 emissions from organic soils in grassland due to drainage.
    """

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
    """
    Calculate the N2O emissions from drainage of organic soils in grassland.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.


    Returns:
    - The calculated N2O emissions from drainage of organic soils in grassland.
    """

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
    """
    Calculate the CO2 emissions from rewetting organic soils in grassland.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.


    Returns:
    - The calculated CO2 emissions from rewetting organic soils in grassland.
    """

    GRASSLAND = Grassland(
        ef_country,
        transition_matrix,
        land_use,
        past_land_use_data,
        "grassland",
        "grassland",
    )

    return GRASSLAND.rewetting_co2_organic_soils_in_grassland()


def rewetting_ch4_organic_soils_in_grassland(
    land_use, past_land_use_data, transition_matrix, ef_country
):
    """
    Calculate the CH4 emissions from rewetting organic soils in grassland.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.

    Returns:
    - The CH4 emissions from rewetting organic soils in grassland.
    """

    GRASSLAND = Grassland(
        ef_country,
        transition_matrix,
        land_use,
        past_land_use_data,
        "grassland",
        "grassland",
    )

    return GRASSLAND.rewetting_ch4_organic_soils_in_grassland()


# Mineral soils

def mineral_soils_co2_grassland_remainging_grassland(
    land_use, past_land_use_data, transition_matrix, ef_country):

    """
    Calculate the CO2 emissions from mineral soils in grassland that remains grassland.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.


    Returns:
    - The calculated CO2 emissions from mineral soils in grassland that remains grassland.
    """
    GRASSLAND = Grassland(
        ef_country,
        transition_matrix,
        land_use,
        past_land_use_data,
        "grassland",
        "grassland",
    )

    return GRASSLAND.mineral_co2_in_grassland()


def mineral_soils_co2_from_forest_to_grassland(
    land_use,
    past_land_use_data,
    transition_matrix_data,
    ef_country,
):
    """
    Calculate CO2 emissions from mineral soils during land use change from forest to grassland.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.


    Returns:
    - The computed CO2 emissions from mineral soils during land use change.
    """
    soc = SOC(
        ef_country,
        land_use,
        past_land_use_data,
        transition_matrix_data,
        "grassland",
        "forest",
    )
    return soc.compute_emissions_from_mineral_soils_in_land_use_change()


def mineral_soils_co2_from_cropland_to_grassland(
    land_use,
    past_land_use_data,
    transition_matrix_data,
    ef_country,
):
    """
    Calculates the CO2 emissions from mineral soils due to land use change from cropland to grassland.

    Args:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.


    Returns:
        float: The computed CO2 emissions from mineral soils in the land use change.

    """
    soc = SOC(
        ef_country,
        land_use,
        past_land_use_data,
        transition_matrix_data,
        "grassland",
        "cropland",
    )

    return soc.compute_emissions_from_mineral_soils_in_land_use_change()


def mineral_soils_n2o_from_forest_to_grassland(
    land_use,
    past_land_use_data,
    transition_matrix_data,
    ef_country,
):
    """
    Calculates the N2O emissions from mineral soils due to land use change from forest to grassland.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.


    Returns:
    - emissions_from_mineralization (float): The calculated N2O emissions from mineral soils.
    """

    soc = SOC(
        ef_country,
        land_use,
        past_land_use_data,
        transition_matrix_data,
        "grassland",
        "forest",
    )

    emissions_from_mineralization = (
        soc.compute_emissions_from_mineral_soils_in_land_use_change() * C_to_N
    )

    return emissions_from_mineralization


# Burning
def burning_co2_grassland(ef_country, transition_matrix, land_use, past_land_use_data):
    """
    Calculate the CO2 emissions from burning grassland.

    Parameters:
        - ef_country (string): Emission factor country.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.

    Returns:
        float: CO2 emissions from burning grassland.
    """
    GRASSLAND = Grassland(
        ef_country,
        transition_matrix,
        land_use,
        past_land_use_data,
        "grassland",
        "grassland",
    )

    return GRASSLAND.burning_co2_grassland() * t_to_kg


def burning_ch4_grassland(ef_country, transition_matrix, land_use, past_land_use_data):
    """
    Calculate the CH4 emissions from burning grassland.

    Parameters:
        - ef_country (string): Emission factor country.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.

    Returns:
        float: CH4 emissions from burning grassland.
    """
    GRASSLAND = Grassland(
        ef_country,
        transition_matrix,
        land_use,
        past_land_use_data,
        "grassland",
        "grassland",
    )

    return GRASSLAND.burning_ch4_grassland() * t_to_kg


def burning_n2o_grassland(ef_country, transition_matrix, land_use, past_land_use_data):
    """
    Calculate the N2O emissions from burning grassland.

     Parameters:
        - ef_country (string): Emission factor country.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.

    Returns:
        float: N2O emissions from burning grassland.

    Raises:
        None

    """
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
    """
    Calculates the total CO2 emission to grassland based on the given parameters. It sums mineral soils CO2
    from forest to grassland and mineral soils CO2 from cropland to grassland.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.

    Returns:
    The total CO2 emission to grassland.
    """

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
    )+ mineral_soils_co2_grassland_remainging_grassland(
        land_use,
        past_land_use_data,
        transition_matrix,
        ef_country,
    )


def total_co2_emission_in_grassland(
    land_use, past_land_use_data, transition_matrix, ef_country
):
    """
    Calculates the total CO2 emission in grassland based on the land use, past land use data,
    transition matrix. It sums the drainage CO2 emission from organic soils and the rewetting.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.

    Returns:
    - float: The total CO2 emission in grassland.
    """

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
    """
    Calculates the total CH4 emission in grassland by summing the drainage CH4 emission from organic soils
    and the rewetting CH4 emission from organic soils.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.

    Returns:
    float: The total CH4 emission in grassland.
    """

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
    """
    Calculate the total CO2 emission from grassland. Includes total CO2 emission to grassland (cropland and forest),
    total CO2 emission in grassland (drainage and rewetting), and burning CO2 emission in grassland.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.

    Returns:
        float: Total CO2 emission from grassland.
    """
    return (
        total_co2_emission_to_grassland(
            land_use, past_land_use_data, transition_matrix, ef_country
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
    """
    Calculate the total CH4 emission in grassland. Includes total CH4 emission in grassland (drainage and rewetting)
    and burning CH4 emission in grassland.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.

    Returns:
        float: The total CH4 emission in grassland.
    """
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
    """
    Calculate the total N2O emission from grassland. Includes N2O emissons from land use change to grassland and
    N2O emissions from burning grassland. N2O emissions from drainage and rewetting are not included as they are
    accounted for in the Agricultural soils category in the national inventory report.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.


    Returns:
    - float: Total N2O emission from grassland.
    """

    return burning_n2o_grassland(
        ef_country, transition_matrix, land_use, past_land_use_data
    ) + mineral_soils_n2o_from_forest_to_grassland(
        land_use,
        past_land_use_data,
        transition_matrix,
        ef_country,
    )
    # + drainage_n2O_organic_soils_in_grassland(
    # land_use, past_land_use_data, transition_matrix, ef_country
    # )


###############################################
#############  WETLAND ########################
###############################################

# Organic soils
# Biomass
def biomass_co2_from_conversion_to_wetland(
    land_use_data, past_land_use_data, transition_matrix, ef_country
):
    """
    Calculate the CO2 removals from conversion to wetland.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.


    Returns:
        float: CO2 removals from conversion to wetland.
    """

    WETLAND = Wetland(
        ef_country,
        transition_matrix,
        land_use_data,
        past_land_use_data,
        "wetland",
        "wetland",
    )

    return WETLAND.co2_removals()


def unmanaged_wetland_ch4_emission(ef_country, transition_matrix, land_use_data, past_land_use_data):
    """
    Calculate the CH4 emissions from unmanaged wetland.

    Parameters:
        - ef_country (string): Emission factor country.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.

    Returns:
        float: The CH4 emissions from unmanaged wetland.
    """
    WETLAND = Wetland(
        ef_country,
        transition_matrix,
        land_use_data,
        past_land_use_data,
        "wetland",
        "wetland",
    )

    return WETLAND.ch4_emissions_unmanaged_and_near_natural()


# Rewetting
def rewetting_co2_organic_soils_in_wetland(
    ef_country, transition_matrix, land_use_data, past_land_use_data
        ):
        ...

# Burning
def burning_co2_wetland(
    ef_country, transition_matrix, land_use_data, past_land_use_data
):
    """
    Calculate the CO2 emissions from burning wetland.

     Parameters:
        - ef_country (string): Emission factor country.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.

    Returns:
        float: CO2 emissions from burning wetland.
    """
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
    """
    Calculate the CH4 emissions from burning wetlands.

    Parameters:
        - ef_country (string): Emission factor country.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.

    Returns:
        float: CH4 emissions from burning wetlands.
    """
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
    """
    Calculate the N2O emissions from burning in wetland areas.

    Parameters:
        - ef_country (string): Emission factor country.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.

    Returns:
        float: N2O emissions from burning in wetland areas.
    """

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
    """
    Calculates the total CO2 emission from wetland based on different factors. Includes CO2 emissions from drainage,
    biomass, and burning.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.

    Returns:
    float: Total CO2 emission from wetland.
    """
    return (biomass_co2_from_conversion_to_wetland(
            land_use_data, past_land_use_data, transition_matrix, ef_country
        )
        + burning_co2_wetland(
            ef_country, transition_matrix, land_use_data, past_land_use_data
        )
    )


def total_ch4_emission_wetland(
    land_use_data, past_land_use_data, transition_matrix, ef_country
):
    """
    Calculate the total CH4 emission from wetlands. Includes CH4 emissions from drainage and burning.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.


    Returns:
        float: Total CH4 emission from wetlands.
    """
    return burning_ch4_wetland(
        ef_country, transition_matrix, land_use_data, past_land_use_data
    ) + unmanaged_wetland_ch4_emission(
        ef_country, transition_matrix, land_use_data, past_land_use_data
    )


def total_n2o_emission_wetland(
    land_use_data, past_land_use_data, transition_matrix, ef_country
):
    """
    Calculate the total N2O emission from wetland. Includes N2O emissions from drainage and burning.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.


    Returns:
        float: Total N2O emission from wetland.
    """
    return burning_n2o_wetland(
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
    """
    Calculates the CO2 emissions from mineral soils due to land use change from forest to cropland.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.


    Returns:
        float: CO2 emissions from mineral soils in the land use change.

    """
    soc = SOC(
        ef_country,
        land_use_data,
        past_land_use_data,
        transition_matrix,
        "cropland",
        "forest",
    )

    return soc.compute_emissions_from_mineral_soils_in_land_use_change()


def mineral_soils_co2_from_grassland_to_cropland(
    land_use_data,
    past_land_use_data,
    transition_matrix,
    ef_country,
):
    """
    Calculates the CO2 emissions from mineral soils due to land use change from grassland to cropland.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.


    Returns:
        float: CO2 emissions from mineral soils in the land use change.

    """
    soc = SOC(
        ef_country,
        land_use_data,
        past_land_use_data,
        transition_matrix,
        "cropland",
        "grassland",
    )

    return soc.compute_emissions_from_mineral_soils_in_land_use_change()




# Burning

# Emissions factor of zero for Co2 burning, IPCC 2006 Table 2.5, notes that the emissions for co2 assumed to be in balance


def burning_ch4_cropland(
    ef_country, transition_matrix, land_use_data, past_land_use_data
):
    """
    Calculate the CH4 emissions from burning cropland.

    Parameters:
        - ef_country (string): Emission factor country.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.


    Returns:
        float: CH4 emissions from burning cropland in kilograms.
    """

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
    """
    Calculate the N2O emissions from burning cropland.

    Parameters:
        - ef_country (string): Emission factor country.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.


    Returns:
        float: N2O emissions from burning cropland.
    """

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
    land_use_data, past_land_use_data, transition_matrix_data, ef_country
):
    """
    Calculates the total CO2 emission from cropland based on the given inputs. Includes conversion of forest to cropland
    and conversion of grassland to cropland.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.

    Returns:
        float: Total CO2 emission from cropland.
    """
    result = mineral_soils_co2_from_forest_to_cropland(
        land_use_data, past_land_use_data, transition_matrix_data, ef_country
    ) + mineral_soils_co2_from_grassland_to_cropland(
        land_use_data, past_land_use_data, transition_matrix_data, ef_country
    )
    return result


def total_ch4_emission_cropland(
    ef_country, transition_matrix, land_use_data, past_land_use_data
):
    """
    Calculate the total CH4 emissions from cropland. Burning is the only source of CH4 emissions from cropland.

    Parameters:
        - ef_country (string): Emission factor country.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
    Returns:
        float: Total CH4 emissions from cropland.
    """
    return burning_ch4_cropland(
        ef_country, transition_matrix, land_use_data, past_land_use_data
    )


def total_n2o_emission_cropland(
    ef_country, transition_matrix, land_use_data, past_land_use_data
):
    """
    Calculate the total N2O emission from cropland. Burning is the only source of N2O emissions from cropland.

    Parameters:
        - ef_country (string): Emission factor country.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.

    Returns:
        float: Total N2O emission from cropland.
    """
    return burning_n2o_cropland(
        ef_country, transition_matrix, land_use_data, past_land_use_data
    )


###################################################################################################################
#############  SETTLEMENT #######################
#################################################


# Organic soils
def drainage_co2_organic_soils_in_settlement(land_use, ef_country):
    """
    Calculate the CO2 emissions from drainage of organic soils in settlements.

    This function estimates the CO2 emissions from drainage of organic soils in settlements.

    See Notes.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - ef_country (string): The emission factor country.

    Returns:
        float: The estimated CO2 emissions from drainage of organic soils in settlements.

    Note:
        The function has not been validated and is not currently used. It overestimates drainage emissions
        because we forest is used as a reference for previous land_use of organic soil converted to settlement.

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
    Calculate the estimated methane emissions from drainage of organic soils in settlements.

    See Notes.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - ef_country (string): The emission factor country.

    Returns:
    - The estimated methane emissions from drainage of organic soils in settlements.

    Note:
        The function has not been validated and is not currently used. This function underestimates
        drainage emissions by using forest as a reference for previous land use of organic soil converted to settlement.

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
    """
    Calculate the CO2 emissions from mineral soils due to forest-to-settlement conversion.

    See Notes.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - ef_country (string): The emission factor country.

    Returns:
        float: The calculated CO2 emissions from mineral soils.

    Notes:
        The function has not been validated and is not currently used.
    """

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
    Calculates the total CO2 emissions from settlement. Includes CO2 emissions from mineral soils and drainage.

    See Notes.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - ef_country (string): The emission factor country.

    Returns:
        float: The total CO2 emissions from settlement activities.

    Notes:
        The function has not been validated and is not currently used.
    """
    return mineral_soils_co2_from_forest_to_settlement(
        land_use, ef_country
    ) + drainage_co2_organic_soils_in_settlement(land_use, ef_country)


def total_ch4_settlement(land_use, ef_country):
    """
    Calculate the total CH4 emissions from settlement areas. Includes CH4 emissions from drainage.

    See Notes.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - ef_country (string): The emission factor country.

    Returns:
        float: The total CH4 emissions from settlement areas.

    Notes:
        The function has not been validated and is not currently used.
    """
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
    """
    Calculates the total CO2 emission by summing the CO2 emissions from different land cover types.
    Types include cropland, forest, grassland, and wetland.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.

    Returns:
        float: Total CO2 emission.

    """
    return (
        total_co2_emission_cropland(
            land_use_data, past_land_use_data, transition_matrix_data, ef_country
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
    """
    Calculate the total CH4 emission by summing the CH4 emissions from different land cover types.
    Types include cropland, forest, grassland, and wetland.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.

    Returns:
        float: Total CH4 emission.

    """
    return (
        total_ch4_emission_wetland(
            land_use_data, past_land_use_data, transition_matrix, ef_country
        )
        + total_ch4_emission_grassland(
            land_use_data, past_land_use_data, transition_matrix, ef_country
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
    """
    Calculate the total N2O emission by summing the N2O emissions from different land cover types.
    Types include cropland, forest, grassland, and wetland.

     Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.
    Returns:
        float: Total N2O emission.

    """
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

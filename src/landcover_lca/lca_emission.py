# -*- coding: utf-8 -*-
"""
CO2, CH4 and N2O emissions from cropland, grassland, forest and wetland (national tree, as goblin_lite calls it).

One function per flux (drainage, rewetting, burning, mineral-soil carbon change, horticultural peat), rolled up by
``total_<gas>_emission_<land use>`` and ``total_<gas>_emission``. Every result is in kg of gas per year. Each function
takes the current and past land use, the transition matrix and the emission factor country. Factors follow NID 2026 /
CRT 2026, otherwise the IPCC; sources are in ``docs/emission_factor_provenance.md``.
"""

import numpy as np
import pandas as pd

from landcover_lca.land_classes.soc import SOC
from landcover_lca.land_classes.wetland import Wetland
from landcover_lca.land_classes.grassland import Grassland
from landcover_lca.land_classes.cropland import Cropland
from landcover_lca.land_classes.forestland import Forest
from landcover_lca.models import Emissions_Factors, Land_Use_Features
from landcover_lca.resource_manager.data_loader import Loader


# scalar vars (unit conversions live in landcover_lca.resource_manager.units)
from landcover_lca.resource_manager.units import C_TO_CO2 as C_to_CO2, KT_TO_KG as kt_to_kg, N2O_N_TO_N2O as N2O_N_to_N2O, T_TO_KG as t_to_kg

C_to_N = 1.0 / 15.0

# N2O from the loss of soil carbon (NID 2026 s.6.3.6.2, eq 11.8 and 11.10; CRT Table 4(III) reproduces them):
#   N mineralised = soil C lost / 15; direct N2O-N = N x EF1; indirect N2O-N = N x FracLEACH x EF5; N2O = N2O-N x 44/28
EF1_SOM = 0.006  # kg N2O-N per kg N mineralised (IPCC 2019 Refinement Table 11.1, wet climate; implied by CRT 4(III) and NID Table 6.9)
FRAC_LEACH = 0.1  # kg N leached per kg N mineralised (Ireland, NID Table 5.7)
EF5 = 0.011  # kg N2O-N per kg N leached or run off (IPCC 2006 Table 11.3; NID p.185)

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
    float: CO2 in kg CO2 per year at the evaluated year (positive = emission, negative = removal). Mineral soils, IPCC Tier 1, NID 2026 eq 6.4.3; see SOC.compute_emissions_from_mineral_soils_in_land_use_change.
    """

    soc = SOC(
        ef_country,
        land_use,
        past_land_use_data,
        transition_matrix_data,
        "forest",
        "cropland",
    )

    return (
        soc.compute_emissions_from_mineral_soils_in_land_use_change()
        * t_to_kg
        * C_to_CO2
    )


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
    float: CO2 in kg CO2 per year at the evaluated year (positive = emission, negative = removal). Mineral soils, IPCC Tier 1, NID 2026 eq 6.4.3; see SOC.compute_emissions_from_mineral_soils_in_land_use_change.
    """

    soc = SOC(
        ef_country,
        land_use,
        past_land_use_data,
        transition_matrix_data,
        "forest",
        "grassland",
    )

    return (
        soc.compute_emissions_from_mineral_soils_in_land_use_change()
        * t_to_kg
        * C_to_CO2
    )


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
    *,
    include_fire_co2=False,
):
    """
    Calculate the total CO2 emission from forest: drained and rewetted organic soils, and wildfire.

    Biomass, dead organic matter and mineral soils are not included: the CBM model covers them.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.
        - include_fire_co2 (bool, keyword only): Include wildfire CO2 (burning_co2_forest). Default False: GOBLIN
          adds CBM forest carbon ("Total Ecosystem" stock change), and CBM's Wildfire disturbance already sends the
          burnt biomass and DOM carbon to the atmosphere (CBM-CFS3 v1.2 User's Guide s.1.8.5, Appendix 6), so adding
          it here would count it twice. The inventory reports it once: CRT Table4 4.A = 4.A stock change + 4(IV)
          wildfire CO2. Set True when no forest carbon model is added, to match the NID (CRT 4(IV).A).
          Fire CH4 and N2O are always included (CBM output used by GOBLIN is carbon only) (FIRE-3).

    Returns:
        float: Total CO2 emission from forest, kg.
    """
    fire = (
        burning_co2_forest(ef_country, transition_matrix, land_use_data, past_land_use_data)
        if include_fire_co2
        else 0.0
    )
    return fire + organic_soils_co2_forest(
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

def mineral_soils_co2_grassland_remaining_grassland(
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
    float: CO2 in kg CO2 per year at the evaluated year (positive = emission, negative = removal). Mineral soils, IPCC Tier 1, NID 2026 eq 6.4.3; see SOC.compute_emissions_from_mineral_soils_in_land_use_change.
    """
    soc = SOC(
        ef_country,
        land_use,
        past_land_use_data,
        transition_matrix_data,
        "grassland",
        "forest",
    )
    return (
        soc.compute_emissions_from_mineral_soils_in_land_use_change()
        * t_to_kg
        * C_to_CO2
    )


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
        float: CO2 in kg CO2 per year at the evaluated year (positive = emission, negative = removal). Mineral soils, IPCC Tier 1, NID 2026 eq 6.4.3; see SOC.compute_emissions_from_mineral_soils_in_land_use_change.

    """
    soc = SOC(
        ef_country,
        land_use,
        past_land_use_data,
        transition_matrix_data,
        "grassland",
        "cropland",
    )

    return (
        soc.compute_emissions_from_mineral_soils_in_land_use_change()
        * t_to_kg
        * C_to_CO2
    )


def n2o_from_soil_carbon_loss(soil_c_loss_t):
    """
    N2O from the mineralisation of soil nitrogen that accompanies a loss of soil carbon
    (NID 2026 eq 11.8 for FSOM and eq 11.10 for leaching and runoff).

    Parameters:
        - soil_c_loss_t (float): soil carbon lost in a year, t C per year (positive = loss).

    Returns:
        float: kg N2O per year, direct plus indirect, = t C x 1000 / 15 (kg N) x (EF1 + FracLEACH x EF5) x 44/28.
        Negative if soil carbon is gained.
    """
    n_mineralised_kg = soil_c_loss_t * C_to_N * t_to_kg
    return n_mineralised_kg * (EF1_SOM + FRAC_LEACH * EF5) * N2O_N_to_N2O


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
    - emissions_from_mineralization (float): N2O from mineral soils in kg N2O per year (direct + indirect, see n2o_from_soil_carbon_loss).
    """

    soc = SOC(
        ef_country,
        land_use,
        past_land_use_data,
        transition_matrix_data,
        "grassland",
        "forest",
    )

    emissions_from_mineralization = n2o_from_soil_carbon_loss(
        soc.compute_emissions_from_mineral_soils_in_land_use_change()
    )

    return emissions_from_mineralization


# Burning
def burning_co2_grassland(ef_country, transition_matrix, land_use, past_land_use_data, include_peat_fire_co2=False):
    """
    CO2 from grassland fires, in kg. 0 by default: not required under the national inventory
    (NID 2026 s.6.5.4, Tier 1 estimates CH4 and N2O only; CRT 4(IV).C.1 CO2 = NO).
    include_peat_fire_co2=True returns CO2 from fires on organic (peat) soil only (IPCC 2013 Wetlands Supplement
    eq 2.8); mineral soil is never charged CO2. See Grassland.burning_co2_grassland.

    Parameters:
        - ef_country (string): Emission factor country.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - land_use (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - include_peat_fire_co2 (bool): False (default) returns 0, as in the inventory.

    Returns:
        float: CO2 emissions from grassland fires (kg).
    """
    GRASSLAND = Grassland(
        ef_country,
        transition_matrix,
        land_use,
        past_land_use_data,
        "grassland",
        "grassland",
    )

    return GRASSLAND.burning_co2_grassland(include_peat_fire_co2) * t_to_kg


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
    )+ mineral_soils_co2_grassland_remaining_grassland(
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
    Calculate the total N2O emission from grassland. Includes N2O emissions from land use change to grassland and
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
    )+ mineral_soils_n2o_from_forest_to_grassland(
        land_use,
        past_land_use_data,
        transition_matrix,
        ef_country,
    )

    #Assumed no additional soils being drained, not included in grassland remaining grassland
    #drainage_n2O_organic_soils_in_grassland(
    #land_use, past_land_use_data, transition_matrix, ef_country
    #)





###############################################
#############  WETLAND ########################
###############################################


# Peat extraction
def horticulture_co2_peat_export(ef_country, year, calibration_year=None):
    """
    Off-site CO2 from horticultural peat (NID 2026 s.6.6.3 p.279 and s.6.6.4.2 p.280; IPCC 2006 Vol 4 eq 7.5).

    Tonnage = exports / frac_horticultural_peat_exported (0.85): 85% of horticultural peat is exported, and the NID
    scales the export figures up to include domestic use. CO2 = tonnage x 0.45 t C/t air-dry peat (IPCC 2006 Vol 4
    Table 7.5, nutrient poor) x 44/12. Exports are the table UN_comtrade_exported_peat (UN Comtrade, HS 2703, Ireland
    to world). The CRT 2026 reports this inside 4.D.1 industrial peat extraction (organic-soil carbon) and the package
    reproduces it exactly for 2020-2024.

    Years in the table use that year's exports. Years after the table use the mean of its last three years (the
    recent level: exports fell from 919 kt in 2020 to 313 kt in 2024). Years before the table, or missing from it,
    raise ValueError.

    This is a national quantity. It is included in total_co2_emission_wetland (and so total_co2_emission) of this
    module, which goblin_lite uses, for the year the land-use data carries. The geo_goblin totals do not include it.

    Parameters:
        ef_country (str): Emission factor country.
        year (int): The year for which the emissions are calculated.
        calibration_year (int, optional): Not used. Kept so existing three-argument calls still work; the table
            decides which years are data.

    Returns:
        float: Off-site CO2 from horticultural peat, kg CO2.

    Raises:
        ValueError: If the year is before the first year of the table, or missing from it.
    """
    data_loader_class = Loader(ef_country)
    emissions_factors = Emissions_Factors(ef_country)
    get = emissions_factors.get_emission_factor_in_emission_factor_data_base
    carbon_to_co2 = get("ef_offsite_carbon_conversion_nutrient_poor")  # kg CO2 per kg air-dry peat
    share_exported = get("frac_horticultural_peat_exported")

    exports = data_loader_class.exported_peat()["Total_kg"].sort_index()
    first, last = int(exports.index.min()), int(exports.index.max())

    if year > last:
        export_weight = exports.iloc[-3:].mean()
    elif pd.isna(exports.get(year)):
        raise ValueError(
            f"No horticultural peat export data for {year}: the table covers {first}-{last}; "
            f"years after {last} use the mean of the last three years."
        )
    else:
        export_weight = exports.loc[year]

    return export_weight / share_exported * carbon_to_co2


# Organic soils
# Biomass
def biomass_co2_from_removals_wetland(
    land_use_data, past_land_use_data, transition_matrix, ef_country
):
    """
    Calculate the CO2 emissions from biomass removals in wetland.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.

    Returns:
    - The CO2 emissions from biomass removals in wetland.
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


# Drainage
def drainage_co2_organic_soils_in_wetland(
    land_use_data, past_land_use_data, transition_matrix, ef_country
):
    """
    Calculate CO2 emissions from drained organic soils in wetland.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.


    Returns:
        float: CO2 emissions from drained organic soils in wetland.
    """

    WETLAND = Wetland(
        ef_country,
        transition_matrix,
        land_use_data,
        past_land_use_data,
        "wetland",
        "wetland",
    )

    return WETLAND.co2_emissions_wetland_drained()

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


def drainage_ch4_organic_soils_in_wetland(
    ef_country, transition_matrix, land_use_data, past_land_use_data
):
    """
    Calculate the CH4 emissions from drainage of organic soils in wetland areas.

    Parameters:
        - ef_country (string): Emission factor country.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.


    Returns:
    - CH4 emissions from organic soils in wetland areas.
    """

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
    """
    Calculate the N2O emissions from drainage of organic soils in wetland areas.

      Parameters:
        - ef_country (string): Emission factor country.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.

    Returns:
    - The N2O emissions from organic soils in wetland areas.
    """

    WETLAND = Wetland(
        ef_country,
        transition_matrix,
        land_use_data,
        past_land_use_data,
        "wetland",
        "wetland",
    )

    return WETLAND.drainage_n2o_organic_soils()

# Rewetting
def rewetting_co2_organic_soils_in_wetland(
    ef_country, transition_matrix, land_use_data, past_land_use_data
        ):
    """
    Calculate the CO2 emissions from rewetting organic soils in wetland.

    Parameters:
        - ef_country (string): Emission factor country.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.

    Returns:
    - The CO2 emissions from rewetting organic soils in wetland.
    """

    WETLAND = Wetland(
        ef_country,
        transition_matrix,
        land_use_data,
        past_land_use_data,
        "wetland",
        "wetland",
    )

    return WETLAND.rewetting_co2_organic_soils()


def rewetting_ch4_organic_soils_in_wetland(
    ef_country, transition_matrix, land_use_data, past_land_use_data
):
    """
    Calculate the CH4 emissions from rewetting organic soils in wetland.

    Parameters:
        - ef_country (string): Emission factor country.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.

    Returns:
    - The CH4 emissions from rewetting organic soils in wetland.
    """

    WETLAND = Wetland(
        ef_country,
        transition_matrix,
        land_use_data,
        past_land_use_data,
        "wetland",
        "wetland",
    )

    return WETLAND.rewetting_ch4_organic_soils_in_wetland()


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
    biomass, burning, rewetting and off-site CO2 from horticultural peat (horticulture_co2_peat_export, national,
    for the year carried by land_use_data.wetland), as the NID reports it in 4.D.1. The geo_goblin total does not
    include horticultural peat.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.

    Returns:
    float: Total CO2 emission from wetland.
    """
    return (
        drainage_co2_organic_soils_in_wetland(
            land_use_data, past_land_use_data, transition_matrix, ef_country
        )
        + biomass_co2_from_removals_wetland(
            land_use_data, past_land_use_data, transition_matrix, ef_country
        )
        + burning_co2_wetland(
            ef_country, transition_matrix, land_use_data, past_land_use_data
        )
        + rewetting_co2_organic_soils_in_wetland(
            ef_country, transition_matrix, land_use_data, past_land_use_data
        )
        + horticulture_co2_peat_export(ef_country, land_use_data.wetland.year)
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
    return drainage_ch4_organic_soils_in_wetland(
        ef_country, transition_matrix, land_use_data, past_land_use_data
    ) + burning_ch4_wetland(
        ef_country, transition_matrix, land_use_data, past_land_use_data
    ) + unmanaged_wetland_ch4_emission(
        ef_country, transition_matrix, land_use_data, past_land_use_data
    )+ rewetting_ch4_organic_soils_in_wetland(
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
    """
    Calculates the CO2 emissions from mineral soils due to land use change from forest to cropland.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.


    Returns:
        float: CO2 in kg CO2 per year at the evaluated year (positive = emission, negative = removal). Mineral soils, IPCC Tier 1, NID 2026 eq 6.4.3; see SOC.compute_emissions_from_mineral_soils_in_land_use_change.

    """
    soc = SOC(
        ef_country,
        land_use_data,
        past_land_use_data,
        transition_matrix,
        "cropland",
        "forest",
    )

    return (
        soc.compute_emissions_from_mineral_soils_in_land_use_change()
        * t_to_kg
        * C_to_CO2
    )


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
        float: CO2 in kg CO2 per year at the evaluated year (positive = emission, negative = removal). Mineral soils, IPCC Tier 1, NID 2026 eq 6.4.3; see SOC.compute_emissions_from_mineral_soils_in_land_use_change.

    """
    soc = SOC(
        ef_country,
        land_use_data,
        past_land_use_data,
        transition_matrix,
        "cropland",
        "grassland",
    )

    return (
        soc.compute_emissions_from_mineral_soils_in_land_use_change()
        * t_to_kg
        * C_to_CO2
    )




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


def _check_total_argument_order(name, land_use_data):
    """Raise TypeError if a total is called with ef_country first (the old order of the cropland CH4 and N2O totals)."""
    if isinstance(land_use_data, str):
        raise TypeError(
            f"{name} takes (land_use_data, past_land_use_data, transition_matrix, ef_country), like every "
            f"total; it was called with ef_country first (the old order of the cropland CH4 and N2O totals)."
        )


def total_ch4_emission_cropland(
    land_use_data, past_land_use_data, transition_matrix, ef_country
):
    """
    Calculate the total CH4 emissions from cropland. Burning is the only source of CH4 emissions from cropland.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.

    Returns:
        float: Total CH4 emissions from cropland, kg.

    Raises:
        TypeError: If called in the old order, (ef_country, transition_matrix, land_use_data,
            past_land_use_data).
    """
    _check_total_argument_order("total_ch4_emission_cropland", land_use_data)
    return burning_ch4_cropland(
        ef_country, transition_matrix, land_use_data, past_land_use_data
    )


def total_n2o_emission_cropland(
    land_use_data, past_land_use_data, transition_matrix, ef_country
):
    """
    Calculate the total N2O emission from cropland. Burning is the only source of N2O emissions from cropland.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.

    Returns:
        float: Total N2O emission from cropland, kg.

    Raises:
        TypeError: If called in the old order, (ef_country, transition_matrix, land_use_data,
            past_land_use_data).
    """
    _check_total_argument_order("total_n2o_emission_cropland", land_use_data)
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

        ef_co2_forest_to_settlement_drainage include onsite and offsite emissions

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
    *,
    include_fire_co2=False,
):
    """
    Calculates the total CO2 emission by summing the CO2 emissions from different land cover types.
    Types include cropland, forest, grassland, and wetland.

    Parameters:
        - land_use_data (landcover_lca.models.LandUseCollection): The current/future land use data.
        - past_land_use_data (landcover_lca.models.LandUseCollection): The past land use data.
        - transition_matrix (landcover_lca.models.TransitionMatrixCategory): The transition matrix.
        - ef_country (string): Emission factor country.
        - include_fire_co2 (bool, keyword only): Include forest wildfire CO2; passed to total_co2_emission_forest.
          Default False (CBM counts it; see total_co2_emission_forest). True to match the NID without CBM.

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
            include_fire_co2=include_fire_co2,
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
            land_use_data, past_land_use_data, transition_matrix, ef_country
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
            land_use_data, past_land_use_data, transition_matrix, ef_country
        )
    )

"""
Description: 
    This file contains utility functions and classes specifically designed for handling and processing land-related data. 
    It includes various utilities that aid in the analysis, manipulation, and management of data related to land cover and associated environmental impact assessments. 

Note: 
    This file is a part of a larger suite of tools aimed at facilitating environmental research and analysis, with a focus on land cover and its implications in ecological studies.

"""


import numpy as np
from landcover_lca.data_loader import Loader
from landcover_lca.models import Emissions_Factors, Land_Use_Features
from landcover_lca.landcover_data_manager import DataManager


class SOC:
    def __init__(
        self,
        ef_country,
        land_use_data,
        past_land_use_data,
        transition_matrix_data,
        current_land_use,
        past_land_use,
    ) -> None:
        """
        Initializes an instance of the SOC (Soil Organic Carbon) class, designed
        for calculating and analyzing the soil organic carbon changes due to land use
        changes. This class integrates data from various sources to compute emissions
        or sequestrations related to land use and land use change.

        Args:
            ef_country (str): The country for which the SOC calculations are to be
                              performed. This is used to load country-specific data
                              and factors.
            land_use_data (LandUseData): An instance of LandUseData class containing
                                         information about the current land use
                                         scenarios and characteristics.
            past_land_use_data (PastLandUseData): An instance of PastLandUseData class
                                                  containing information about the
                                                  historical or past land use scenarios.
            transition_matrix_data (TransitionMatrixData): An instance of
                                                           TransitionMatrixData class
                                                           containing the data for
                                                           transitions between different
                                                           land use categories over time.
            current_land_use (str): The current land use category for which the SOC
                                    changes are being assessed.
            past_land_use (str): The past land use category from which the current land
                                 use category was converted.
        """
        self.data_loader_class = Loader(ef_country)
        self.ipcc_soil_class_SOC = self.data_loader_class.ipcc_soc_factors()
        self.land_use_data = land_use_data
        self.past_land_use_data = past_land_use_data
        self.transition_matrix_data = transition_matrix_data
        self.land_use_features = Land_Use_Features(ef_country)
        self.current_land_use = current_land_use
        self.past_land_use = past_land_use
        self.year_range = self.get_time_period()

    def get_time_period(self):
        """
        Calculates the time period between the current and past land use data.

        Returns:
            int: The time period in years.
        """
        years = tuple(
            (
                self.land_use_data.__getattribute__(self.current_land_use).year,
                self.past_land_use_data.__getattribute__(self.current_land_use).year,
            )
        )

        scenario_period = years[0] - years[1]

        return scenario_period

    def compute_SOC_ref_for_land_use(self):
        """
        Computes the reference SOC for the current land use category.

        Returns:
            float: The reference SOC value.
        """
        return np.sum(
            self.ipcc_soil_class_SOC["Proportion"] * self.ipcc_soil_class_SOC["SOCref"]
        )

    def compute_land_use_change_total_area(self):
        """
        Computes the total area converted from the past land use to the current land use.

        Returns:
            float: The annual area converted.
        """
        land_use_total_area = self.transition_matrix_data.__dict__[
            f"{self.past_land_use}_to_{self.current_land_use}"
        ]

        try:
            land_use_annual_area = land_use_total_area / self.year_range

            return land_use_annual_area

        except ZeroDivisionError:
            return 0

    def compute_emission_factor_from_mineral_soils(self, land_use_name):
        """
        Computes the emission factor from mineral soils for a given land use category.

        Args:
            land_use_name (str): The name of the land use category.

        Returns:
            float: The emission factor from mineral soils.
        """
        FLU = (
            self.land_use_features.get_landuse_features_in_land_use_features_data_base(
                "FLU", land_use_name
            )
        )
        FMG = (
            self.land_use_features.get_landuse_features_in_land_use_features_data_base(
                "FMG", land_use_name
            )
        )
        FI = self.land_use_features.get_landuse_features_in_land_use_features_data_base(
            "FI", land_use_name
        )
        Adjustement_factor = (
            self.land_use_features.get_landuse_features_in_land_use_features_data_base(
                "Adjustement_factor", land_use_name
            )
        )

        SOC_ref = self.compute_SOC_ref_for_land_use()

        return SOC_ref * Adjustement_factor

    def compute_emissions_from_mineral_soils_in_land_use_change(self):
        """
        Computes the emissions from mineral soils during land use change.

        Returns:
            float: The total emissions from mineral soils.
        """
        EF_SOC_previous_land_use = self.compute_emission_factor_from_mineral_soils(
            self.past_land_use
        )

        EF_SOC_current_land_use = self.compute_emission_factor_from_mineral_soils(
            self.current_land_use
        )

        annual_area = self.compute_land_use_change_total_area()

        transition_period = 20

        soc = 0
        if annual_area:
            for year in range(self.year_range):
                if year < 20:
                    soc += (
                        annual_area
                        * (EF_SOC_current_land_use - EF_SOC_previous_land_use)
                    ) / transition_period
                else:
                    return soc
        else:
            return soc


class LandUse:
    """
    The LandUse class is designed to analyze and calculate various aspects of
    land use and land use change, focusing on their environmental impact in
    terms of emissions and land area transitions.

    This class processes data related to different land use categories,
    considering both historical (past) and future (projected) land use scenarios,
    to understand the dynamics of land use changes and their environmental
    consequences.

    Args:
        ef_country (str): The country for which the land use data is being
                          analyzed. Essential for loading country-specific data
                          and emission factors.
        transition_matrix_data (TransitionMatrixData): An instance of
                                                       TransitionMatrixData class
                                                       containing data for
                                                       transitions between
                                                       different land use
                                                       categories over time.
        land_use_data: Land use transition data for future scenarios.
        past_land_use_data: Data representing current or past land use scenarios.
        past_land_use (str, optional): The past land use category. Defaults to None.
        current_land_use (str, optional): The current/future land use category. Defaults
                                          to None.
    """

    def __init__(
        self,
        ef_country,
        transition_matrix_data,
        land_use_data,
        past_land_use_data,
        past_land_use=None,
        current_land_use=None,
    ) -> None:
        self.data_loader_class = Loader(ef_country)
        self.current_land_use = current_land_use
        self.past_land_use = past_land_use
        self.emissions_factors = Emissions_Factors(ef_country)
        self.forest_age_data = self.data_loader_class.national_forest_inventory()
        self.transition_matrix_data = transition_matrix_data
        self.land_use_data = land_use_data
        self.past_land_use_data = past_land_use_data
        self.year_range = self.get_time_period()
        self.annual_area = self.compute_land_use_annual_area()
        self.combined_area = self.compute_total_land_use_area()
        self.total_transition_area = self.get_total_transition_area()

    def get_time_period(self):
        """
        Calculates the time period between the current (or future) and past land
        use scenarios. This period helps in understanding the duration over which
        land use changes have occurred or are projected to occur.

        Returns:
            int: The time period in years between the current (or future) and past
                 land use data.
        """
        years = tuple(
            (
                self.land_use_data.__getattribute__(self.current_land_use).year,
                self.past_land_use_data.__getattribute__(self.current_land_use).year,
            )
        )

        scenario_period = years[0] - years[1]

        return scenario_period

    def compute_land_use_annual_area(self):
        """
        Calculates the annual area that has been or is projected to be converted
        from the past land use to the current (or future) land use category.
        This calculation is crucial for understanding the rate of land use change
        on an annual basis.

        Returns:
            float: The annual area converted (in hectares) from past
                   to current (or future) land use, averaged over the time period.
        """

        land_use_total_area = self.transition_matrix_data.__dict__[
            f"{self.past_land_use}_to_{self.current_land_use}"
        ]

        try:
            land_use_annual_area = land_use_total_area / self.year_range

            return land_use_annual_area

        except ZeroDivisionError:
            return 0

    def get_total_transition_area(self):
        """
        Retrieves the total area that has transitioned or is projected to transition
        from the past land use category to the current (or future) land use category.
        This measure is vital for assessing the scale of land use change.

        Returns:
            float: The total transition area (in hectares) between
                   the past and current (or future) land use categories.
        """
        return self.transition_matrix_data.__dict__[
            f"{self.past_land_use}_to_{self.current_land_use}"
        ]

    def compute_total_land_use_area(self):
        """
        Computes the total area covered by the current (or future) land use category.
        This measurement provides insight into the extent of a specific land use type
        within the selected region or country.

        Returns:
            float: The total area (in hectares) covered by the
                   current (or future) land use category.
        """
        land_use_total_area = self.land_use_data.__getattribute__(
            self.current_land_use
        ).area_ha

        return land_use_total_area


class Wetland(LandUse):
    """
    A class representing a wetland land use.

    Attributes:
        ef_country (str): The country for which the emissions factors are calculated.
        transition_matrix_data (TransitionMatrixData): The transition matrix data.
        land_use_data (LandUseData): The land use data.
        past_land_use_data (PastLandUseData): The past land use data.
        past_land_use (str): The past land use.
        current_land_use (str): The current land use.
        current_area_drained (float): The current area drained in hectares.

    Methods:
        co2_removals(): Calculates the carbon removals from the wetland.
        co2_emissions_wetland_drained(): Calculates the CO2 emissions from wetland drainage.
        drainage_ch4_organic_soils(): Calculates the CH4 emissions from organic soils due to drainage.
        drainage_n2o_organic_soils(): Calculates the N2O emissions from organic soils due to drainage.
        rewetting_co2_organic_soils(): Estimates the CO2 emissions from rewetting of wetland (not implemented).
        rewetting_ch4_organic_soils_in_wetland(): Estimates the CH4 emissions from rewetting of wetland (not implemented).
        burning_co2_wetland(): Calculates the CO2 emissions from burning of wetland.
        burning_ch4_wetland(): Calculates the CH4 emissions from burning of wetland.
        burning_n2o_wetland(): Calculates the N2O emissions from burning of wetland.
    """

    def __init__(
        self,
        ef_country,
        transition_matrix_data,
        land_use_data,
        past_land_use_data,
        past_land_use,
        current_land_use,
    ) -> None:
        super().__init__(
            ef_country,
            transition_matrix_data,
            land_use_data,
            past_land_use_data,
            past_land_use,
            current_land_use,
        )

        self.current_area_drained = (
            self.land_use_data.wetland.area_ha
            * self.land_use_data.wetland.share_peat_extraction
        )

    def co2_removals(self):
        """
        Calculate the amount of CO2 removals per year for a given area.
        return 0.6t C per year for 5 years for area drained.

        Returns:
            float: The total amount of CO2 removals over the specified year range.
        """

        biomass_removal_factor = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_peatland_to_wetland_biomass"
            )
        )

        carbon_sequestration = 0

        if self.annual_area != 0:
            if self.year_range <= 5:
                for year in range(5):
                    carbon_sequestration += (self.annual_area * (year + 1)) * (
                        biomass_removal_factor / year + 1
                    )

                return carbon_sequestration
            else:
                for year in range(len(self.year_range)):
                    carbon_sequestration += (self.annual_area * (year + 1)) * (
                        biomass_removal_factor / year + 1
                    )

                return carbon_sequestration

        else:
            return carbon_sequestration

    def co2_emissions_wetland_drained(self):
        """
        Calculates the carbon dioxide (CO2) emissions resulting from the drainage of wetlands.
        Wetland drainage can lead to significant CO2 emissions, primarily due to the exposure
        and decomposition of organic matter that was previously submerged and preserved
        under waterlogged conditions.

        This method calculates CO2 emissions by considering two main emission factors:
        emissions from the drainage site itself and emissions due to dissolved organic carbon
        (DOC). DOC refers to organic carbon released into water bodies as a result of wetland
        drainage.

        Emission factors are sourced from a country-specific database (`ef_country`) of
        emission factors, considering the unique characteristics of wetlands in different
        regions.

        Returns:
            float: The calculated CO2 emissions (in a suitable unit like kg or tonnes) from
                wetland drainage. The calculation is based on the current area of drained
                wetland and the sum of the two emission factors, one for on-site emissions
                and the other for emissions due to DOC.

        Notes:
            - `ef_co2_wetland_drainage_on_site` refers to the emission factor for on-site
            CO2 emissions due to wetland drainage.
            - `ef_co2_wetland_drainage_DOC` refers to the emission factor for CO2 emissions
            related to dissolved organic carbon due to wetland drainage.
            - `current_area_drained` is determined based on the data of wetland
            area and the proportion used for peat extraction, which contributes to the
            drainage.
        """
        ef_co2_wetland_drainage_on_site = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_wetland_drainage_on_site"
            )
        )
        ef_co2_wetland_drainage_DOC = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_wetland_drainage_DOC"
            )
        )

        current_area_drained = (
            self.past_land_use_data.wetland.area_ha
            * self.past_land_use_data.wetland.share_peat_extraction
        )

        return current_area_drained * (
            ef_co2_wetland_drainage_on_site + ef_co2_wetland_drainage_DOC
        )

    def drainage_ch4_organic_soils(self):
        """
        Calculates the methane (CH4) emissions resulting from the drainage of organic soils,
        such as peatlands. Drainage of such soils can significantly increase methane
        emissions, a potent greenhouse gas, due to the exposure of previously waterlogged
        organic matter to aerobic conditions, leading to its decomposition.

        The method considers different emission factors for peatland that is drained
        for land use (e.g., agriculture) and for drainage via ditches.

        Emission factors are retrieved from a database of emission factors specific
        to the country (`ef_country`) provided at the class initialization.

        Returns:
            float: The calculated CH4 emissions from organic soils due to drainage.
                This is based on the current area of drained land, the proportion of land drained by ditches,
                and the respective emission factors for each type of drainage.

        Notes:
            - `ef_ch4_drainage_peatland_land` refers to the emission factor for peatland
            drained for land use.
            - `ef_ch4_drainage_peatland_ditch` refers to the emission factor for peatland
            drained via ditches.
            - `frac_ditch` represents the fraction of the total drained area that is
            drained by ditches.
            - `self.current_area_drained` is the total current area of drained organic soil.
        """
        ef_ch4_drainage_peatland_land = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_ch4_wetland_drainage_land"
            )
        )
        ef_ch4_drainage_peatland_ditch = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_ch4_wetland_drainage_ditch"
            )
        )

        frac_ditch = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "frac_ditch"
            )
        )

        return self.current_area_drained * (
            (1.0 - frac_ditch) * ef_ch4_drainage_peatland_land
            + frac_ditch * ef_ch4_drainage_peatland_ditch
        )

    def drainage_n2o_organic_soils(self):
        """
        Calculates the nitrous oxide (N2O) emissions resulting from the drainage of organic
        soils. N2O, a potent greenhouse gas, is often released in significant amounts when
        wetlands, especially peatlands, are drained. The drainage process alters the soil
        conditions, promoting conditions favorable for N2O production.

        This method calculates N2O emissions specifically for the drainage of wetland.

        The emission factor is obtained from a country-specific database of emission
        factors, ensuring the calculation is tailored to the regional characteristics
        of the land use change.

        Returns:
            float: The calculated N2O emissions resulting from the drainage of organic soils.
        """
        ef_n2o_drainage_wetland_to_peatland = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_n2o_wetland_drainage"
            )
        )

        return self.current_area_drained * ef_n2o_drainage_wetland_to_peatland

    def rewetting_co2_organic_soils(self):
        """
        REturn nothing for the time being as we are estimating the rewetting of grassland and not wetlands
        """
        ef_co2_peatland_to_wetland_rewetting_on_site = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_wetland_rewetting_on_site"
            )
        )
        ef_co2_peatland_to_wetland_rewetting_DOC = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_wetland_rewetting_DOC"
            )
        )

    def rewetting_ch4_organic_soils_in_wetland(self):
        """
        REturn nothing for the time being as we are estimating the rewetting of grassland and not wetlands
        """

        ef_ch4_peatland_to_wetland_rewetting = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_ch4_wetland_rewetting"
            )
        )

    def burning_co2_wetland(self):
        """
        Calculates the carbon dioxide (CO2) emissions resulting from the burning of wetland
        vegetation and organic matter. This method focuses on CO2 emissions due to the
        combustion of wetland biomass, which can occur in various scenarios, such as
        land management practices or wildfires.

        The calculation incorporates two key emission factors: one for the burning of
        wetland fuels (biomass) and another that represents the emission factors
        (Gef) for CO2 emissions from wetland burning. These factors are sourced from
        a country-specific database, reflecting regional variations in wetland
        composition and burning practices.

        The total CO2 emissions are estimated by multiplying the total combined area
        of the wetland, the proportion of the wetland that is burnt, and the product
        of the two emission factors.

        Returns:
            float: The calculated CO2 emissions (in tonnes) from the burning of wetlands.
                The calculation is based on the combined wetland area, the share of
                wetlands burnt, and the specific emission factors for wetland fuel
                burning and general CO2 emissions.

        Notes:
            - `ef_wetland_fuel_burning` refers to the emission factor for the burning
            of wetland fuels.
            - `ef_co2_wetland_Gef` is the emission factor for CO2 emissions from
            wetland burning.
            - `self.combined_area` is the total area of wetlands being considered.
            - `self.land_use_data.wetland.share_burnt` indicates the proportion of the
            wetland area that undergoes burning.
        """
        ef_wetland_fuel_burning = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_wetland_fuel_burning"
            )
        )
        ef_co2_wetland_Gef = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_wetland_Gef"
            )
        )

        return (
            (self.combined_area * self.land_use_data.wetland.share_burnt)
            * ef_wetland_fuel_burning
            * ef_co2_wetland_Gef
            * 10**-3
        )

    def burning_ch4_wetland(self):
        """
        Calculates the methane (CH4) emissions resulting from the burning of wetland
        vegetation and organic matter. This method assesses CH4 emissions, a potent
        greenhouse gas, released during the combustion of wetland biomass, which can
        occur due to natural fires, agricultural burning, or other human activities.

        The calculation involves two primary emission factors: one for the combustion
        of wetland fuels (biomass) and another representing the emission factor
        (Gef) for CH4 emissions specifically from wetland burning. These emission factors
        are sourced from a country-specific database to account for regional differences
        in wetland burning characteristics and fuel types.

        The total CH4 emissions are estimated by multiplying the combined wetland area,
        the proportion of wetland that is burnt, and the product of the two emission
        factors.

        Returns:
            float: The calculated CH4 emissions (in tonnes) from the burning of wetlands.
                This is determined by considering the combined wetland area, the share
                of wetlands burnt, and the specific emission factors for wetland fuel
                burning and general CH4 emissions.

        Notes:
            - `ef_wetland_fuel_burning` refers to the emission factor for the burning
            of wetland fuels in terms of CH4.
            - `ef_ch4_wetland_Gef` is the emission factor for CH4 emissions from
            wetland burning.
            - `self.combined_area` represents the total area of wetlands being analyzed.
            - `self.land_use_data.wetland.share_burnt` indicates the fraction of the
            wetland area that undergoes burning.
        """
        ef_wetland_fuel_burning = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_wetland_fuel_burning"
            )
        )
        ef_ch4_wetland_Gef = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_ch4_wetland_Gef"
            )
        )

        return (
            (self.combined_area * self.land_use_data.wetland.share_burnt)
            * ef_wetland_fuel_burning
            * ef_ch4_wetland_Gef
            * 10**-3
        )

    def burning_n2o_wetland(self):
        """
        Calculates the nitrous oxide (N2O) emissions resulting from the burning of wetland
        vegetation and organic matter. Wetland burning can be a significant source of N2O,
        a potent greenhouse gas, especially when it involves the combustion of peat and
        other nitrogen-rich organic materials.

        This method incorporates two emission factors: one for the combustion of wetland
        fuels (biomass) and another for the emission factor (Gef) specific to N2O
        emissions from wetland burning. These emission factors are obtained from a
        country-specific database, which accounts for variations in wetland types and
        burning practices across different regions.

        The total N2O emissions are estimated by multiplying the combined area of the
        wetland, the proportion of the wetland that is burnt, and the product of the two
        emission factors.

        Returns:
            float: The calculated N2O emissions (in tonnes) from the burning of wetlands.
                The computation takes into account the combined wetland area, the
                proportion of wetlands burnt, and the respective emission factors for
                wetland fuel burning and general N2O emissions.

        Notes:
            - `ef_wetland_fuel_burning` refers to the emission factor for the burning
            of wetland fuels in terms of N2O.
            - `ef_n2o_wetland_Gef` is the emission factor for N2O emissions from
            wetland burning.
            - `self.combined_area` is the total area of wetlands being considered in the
            calculation.
            - `self.land_use_data.wetland.share_burnt` represents the percentage of the
            wetland area that undergoes burning.
        """
        ef_wetland_fuel_burning = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_wetland_fuel_burning"
            )
        )
        ef_n2o_wetland_Gef = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_n2o_wetland_Gef"
            )
        )

        return (
            (self.combined_area * self.land_use_data.wetland.share_burnt)
            * ef_wetland_fuel_burning
            * ef_n2o_wetland_Gef
            * 10**-3
        )


class Grassland(LandUse):
    """
    A class representing grassland land use.

    Attributes:
    - ef_country: The country-specific emission factors.
    - transition_matrix_data: The transition matrix data.
    - land_use_data: The land use data.
    - past_land_use_data: The past land use data.
    - past_land_use: The past land use.
    - current_land_use: The current land use.
    - current_area: The current area of grassland.
    - current_area_drained: The current area of drained grassland.

    Methods:
    - drainage_co2_organic_soils_in_grassland: Calculate CO2 emissions from drainage of organic soils in grassland.
    - drainage_ch4_organic_soils_in_grassland: Calculate CH4 emissions from drainage of organic soils in grassland.
    - drainage_n2O_organic_soils_in_grassland: Calculate N2O emissions from drainage of organic soils in grassland.
    - rewetting_co2_organic_soils_in_grassland: Calculate CO2 emissions from rewetting of organic soils in grassland.
    - rewetting_ch4_organic_soils_in_grassland: Calculate CH4 emissions from rewetting of organic soils in grassland.
    - burning_co2_grassland: Calculate CO2 emissions from burning of grassland.
    - burning_ch4_grassland: Calculate CH4 emissions from burning of grassland.
    - burning_n2o_grassland: Calculate N2O emissions from burning of grassland.
    """

    def __init__(
        self,
        ef_country,
        transition_matrix_data,
        land_use_data,
        past_land_use_data,
        past_land_use,
        current_land_use,
    ) -> None:
        super().__init__(
            ef_country,
            transition_matrix_data,
            land_use_data,
            past_land_use_data,
            past_land_use,
            current_land_use,
        )

        self.current_land_use = "grassland"
        self.current_area = self.land_use_data.grassland.area_ha

        self.current_area_drained = (
            self.land_use_data.grassland.area_ha
            * self.land_use_data.grassland.share_organic
        )

    def drainage_co2_organic_soils_in_grassland(self):
        """
        Calculates the carbon dioxide (CO2) emissions resulting from the drainage of organic
        soils in grassland areas. Draining organic soils can lead to significant CO2 emissions.
        This process exposes previously waterlogged organic matter to oxygen, accelerating its
        decomposition and releasing stored carbon into the atmosphere.

        This method focuses specifically on CO2 emissions from on-site sources in grasslands
        where organic soils have been drained. The emission factor used for this calculation
        is tailored to the specific conditions of drained grasslands, reflecting the typical
        rate of CO2 emissions per unit area for such land use change.

        The emission factor is obtained from a country-specific database of emission factors,
        ensuring the calculation is representative of regional characteristics and land
        management practices.

        Returns:
            float: The calculated CO2 emissions resulting from the drainage of organic soils
                in grassland areas. The emissions are based on the current area of drained
                land and the specific emission factor for CO2 emissions from grassland drainage.

        Notes:
            - `ef_co2_grassland_drainage_on_site` refers to the emission factor for CO2
            emissions specific to the drainage of organic soils in grassland areas.
            - `self.current_area_drained` indicates the total area of organic soils in
            grasslands that have been drained, which is used in the emissions calculation.
        """
        ef_co2_grassland_drainage_on_site = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_grassland_drainage_on_site"
            )
        )

        return self.current_area_drained * ef_co2_grassland_drainage_on_site

    def drainage_ch4_organic_soils_in_grassland(self):
        """
        Calculates the methane (CH4) emissions resulting from the drainage of organic soils
        in grassland areas. The drainage of organic soils can significantly
        increase CH4 emissions due to the exposure of previously waterlogged organic matter
        to conditions that promote methane production.

        This method estimates CH4 emissions for two types of drainage in grasslands: direct
        land drainage and drainage through ditches. Each type of drainage has its own emission
        factor, reflecting the different conditions and methane production rates associated
        with these drainage methods.

        Emission factors are sourced from a country-specific database, ensuring that the
        emissions estimation is relevant to the regional characteristics of grassland drainage.

        Returns:
            float: The calculated CH4 emissions from organic soils in grassland areas.
            The emissions are based on the current area of drained land and a combination
            of the emission factors for land drainage and ditch drainage.

        Notes:
            - `ef_ch4_grassland_drainage_land` refers to the emission factor for CH4
            emissions from direct land drainage in grasslands.
            - `ef_ch4_grassland_drainage_ditch` refers to the emission factor for CH4
            emissions from drainage through ditches in grasslands.
            - `frac_ditch` is the fraction of the drained area in grasslands that is
            drained through ditches, used to weight the emission factors appropriately.
            - `self.current_area_drained` indicates the total area of organic soils in
            grasslands that have been drained.
        """
        ef_ch4_grassland_drainage_land = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_ch4_grassland_drainage_land"
            )
        )
        ef_ch4_grassland_drainage_ditch = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_ch4_grassland_drainage_ditch"
            )
        )

        frac_ditch = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "frac_ditch"
            )
        )

        return self.current_area_drained * (
            (1.0 - frac_ditch) * ef_ch4_grassland_drainage_land
            + frac_ditch * ef_ch4_grassland_drainage_ditch
        )

    def drainage_n2O_organic_soils_in_grassland(self):
        """
        Calculates the nitrous oxide (N2O) emissions resulting from the drainage of organic
        soils in grassland areas. Drainage of organic soils in grasslands can lead to increased N2O emissions.
        This is due to the changes in soil conditions that promote nitrification and denitrification processes,
        which are major sources of N2O emissions.

        This method estimates N2O emissions by applying an emission factor specific to
        grassland drainage.

        The emission factor is obtained from a country-specific database of emission factors,
        ensuring the calculation takes into account regional variations in soil types,
        grassland management practices, and climatic conditions.

        Returns:
            float: The calculated N2O emissionsresulting from the drainage of organic soils in grassland areas.
            The emissions are based on the current area of drained land and the specific emission factor for
            N2O emissions from grassland drainage.

        Notes:
            - `ef_n2o_grassland_drainage` refers to the emission factor for N2O emissions
            from the drainage of organic soils in grassland areas.
            - `self.current_area_drained` is the total area of organic soils in grasslands
            that have been drained, which is used in the calculation for estimating the
            total N2O emissions.
        """
        ef_n2o_grassland_drainage = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_n2o_grassland_drainage"
            )
        )

        return self.current_area_drained * ef_n2o_grassland_drainage

    def rewetting_co2_organic_soils_in_grassland(self):
        """
        Calculates the carbon dioxide (CO2) emissions reductions resulting from the rewetting
        of drained organic soils in grassland areas. Rewetting previously drained organic
        soils can significantly reduce CO2 emissions by restoring waterlogged conditions,
        which slow down the decomposition of organic matter and carbon release.

        This method considers two key emission reduction factors: the reduction of direct
        on-site CO2 emissions due to rewetting and the reduction of CO2 emissions related
        to dissolved organic carbon (DOC). The latter factor accounts for the decrease in
        carbon released into water bodies as a result of rewetting.

        The emission reduction factors are sourced from a country-specific database, ensuring
        that the calculation is tailored to the regional characteristics of grassland
        management and soil types.

        Returns:
            float: The calculated CO2 emissions reductions resulting from the rewetting of
            organic soils in grassland areas. The reductions are based on the total area
            undergoing transition from drained to rewetted conditions and the sum of the two emission reduction
            factors for on-site emissions and DOC-related emissions.

        Notes:
            - `ef_co2_grassland_rewetting_on_site` refers to the emission reduction factor
            for direct on-site CO2 emissions due to grassland rewetting.
            - `ef_co2_grassland_rewetting_DOC` refers to the emission reduction factor for
            CO2 emissions related to dissolved organic carbon due to grassland rewetting.
            - `self.total_transition_area` is the total area of grasslands undergoing
            transition from drained to rewetted conditions, used in the calculation for
            estimating total CO2 emissions reductions.
        """
        ef_co2_grassland_rewetting_on_site = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_grassland_rewetting_on_site"
            )
        )
        ef_co2_grassland_rewetting_DOC = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_grassland_rewetting_DOC"
            )
        )

        return (
            ef_co2_grassland_rewetting_on_site + ef_co2_grassland_rewetting_DOC
        ) * self.total_transition_area

    def rewetting_ch4_organic_soils_in_grassland(self):
        """
        Calculates the methane (CH4) emissions resulting from the rewetting of drained
        organic soils in grassland areas. Rewetting such soils, particularly in areas
        previously used as peatlands or other wetlands, can lead to an increase in CH4
        emissions. This is due to the creation of anaerobic conditions favorable for
        methanogenesis (methane production) in waterlogged soils.

        This method utilizes an emission factor that specifically quantifies the rate
        of CH4 emissions per unit area resulting from the rewetting of organic soils in
        grassland environments. The emission factor is sourced from a country-specific
        database, accounting for variations in soil types, previous land use practices,
        and climatic conditions.

        The total CH4 emissions are estimated based on the total area of grasslands
        undergoing transition from drained to rewetted conditions and the emission
        factor for grassland rewetting.

        Returns:
            float: The calculated CH4 emissions resulting from the rewetting of organic
            soils in grassland areas.
            The emissions are based on the total transition area and the specific
            emission factor for CH4 emissions from grassland rewetting.

        Notes:
            - `ef_ch4_grassland_rewetting` refers to the emission factor for CH4 emissions
            from the rewetting of organic soils in grassland areas.
            - `self.total_transition_area` is the total area of grasslands undergoing
            transition from drained to rewetted conditions, used in the emissions
            calculation.
        """
        ef_ch4_grassland_rewetting = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_ch4_grassland_rewetting"
            )
        )

        return ef_ch4_grassland_rewetting * self.total_transition_area

    def burning_co2_grassland(self):
        """
        Calculates the carbon dioxide (CO2) emissions resulting from the burning of grasslands.
        This method assesses CO2 emissions from two types of soil in grasslands: mineral soils
        and drained organic soils. The emission calculation is based on the formula
        𝐿𝑓𝑖𝑟𝑒 = 𝐴 ∙ 𝑀𝐵 ∙ 𝐶𝑓 ∙ 𝐺𝑒𝑓 ∙ 10^−3, where A is the area, MB is the biomass,
        Cf is the combustion factor, and Gef is the emission factor.

        The combustion factor (Cf) is assumed to be 1.0, indicating that all available fuel
        (biomass) is burned. The method involves multiplying the area of grassland burned by
        the emission factors for CO2 emissions from both mineral and drained organic soils.

        Emission factors are sourced from a country-specific database, reflecting regional
        variations in grassland composition and burning characteristics.

        Returns:
            float: The calculated CO2 emissions (in tonnes) from the burning of grasslands,
                including both mineral soils and drained organic soils. The calculation
                considers the area of each soil type that is burned and their respective
                emission factors.

        Notes:
            - `ef_wildfire_GEF_co2_mineral` and `ef_wildfire_GEF_co2_drained` are the emission factors for CO2 emissions
            from the burning of mineral soils and drained organic soils in grasslands, respectively.

            - The area calculations for each soil type are based on the proportion of grassland
            area that is burnt and the share of each soil type in the grassland area.
        """

        ef_wildfire_MB_time_CF_mineral_soil_grassland = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_wildfire_GEF_ch4_mineral_soil_grassland"
            )
        )
        ef_wildfire_MB_time_CF_drained_organic_soil_grassland = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_wildfire_MB_time_CF_drained_organic_soil_grassland"
            )
        )
        ef_wildfire_MB_time_CF_wet_organic_soil_grassland = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_wildfire_MB_time_CF_wet_organic_soil_grassland"
            )
        )

        ef_wildfire_GEF_co2_mineral = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_wildfire_GEF_co2_mineral_soil_grassland"
            )
        )
        ef_wildfire_GEF_co2_wet = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_wildfire_GEF_co2_wet_organic_soil_grassland"
            )
        )
        ef_wildfire_GEF_co2_drained = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_wildfire_GEF_co2_drained_organic_soil_grassland"
            )
        )

        fire_mineral_soil = (
            (
                self.land_use_data.grassland.area_ha
                * self.land_use_data.grassland.share_burnt
                * self.land_use_data.grassland.share_mineral
            )
            * ef_wildfire_MB_time_CF_mineral_soil_grassland
            * ef_wildfire_GEF_co2_mineral
            * 10**-3
        )
        # fire_undrained_organic_soil = (
        # (
        # self.land_use_data.grassland.area_ha
        # * self.land_use_data.grassland.share_burnt
        # * (
        #  self.land_use_data.grassland.share_organic
        # + self.land_use_data.grassland.share_organic_mineral
        # )
        # )
        # * ef_wildfire_MB_time_CF_wet_organic_soil_grassland
        # * ef_wildfire_GEF_co2_wet
        # * 10**-3
        # )
        fire_drained_organic_soil = (
            (
                self.land_use_data.grassland.area_ha
                * self.land_use_data.grassland.share_burnt
                * self.land_use_data.grassland.share_organic
            )
            * ef_wildfire_MB_time_CF_drained_organic_soil_grassland
            * ef_wildfire_GEF_co2_drained
            * 10**-3
        )

        # return (
        # fire_mineral_soil + fire_undrained_organic_soil + fire_drained_organic_soil
        # )
        return fire_mineral_soil + fire_drained_organic_soil

    def burning_ch4_grassland(self):
        """
        Calculates the methane (CH4) emissions resulting from the burning of grasslands.
        This method evaluates CH4 emissions from two types of soil in grasslands: mineral
        soils and drained organic soils. The calculation formula used is
        𝐿𝑓𝑖𝑟𝑒 = 𝐴 ∙ 𝑀𝐵 ∙ 𝐶𝑓 ∙ 𝐺𝑒𝑓 ∙ 10^−3, where A represents the area, MB is the biomass,
        Cf is the combustion factor, and Gef is the emission factor.

        The combustion factor (Cf) is assumed to be 1.0, signifying that all available
        fuel (biomass) is burned. The method involves multiplying the area of grassland
        burned by the emission factors for CH4 emissions from both mineral and drained
        organic soils.

        Emission factors are obtained from a country-specific database, which takes into
        account regional differences in grassland composition and burning characteristics.

        Returns:
            float: The calculated CH4 emissions (in tonnes) from the burning of grasslands,
                comprising both mineral soils and drained organic soils. The calculation
                involves considering the area of each soil type that is burned and their
                respective emission factors.

        Notes:
            - `ef_wildfire_GEF_ch4_mineral` and `ef_wildfire_GEF_ch4_drained` are the emission
            factors for CH4 emissions from the burning of mineral soils and drained organic soils
            in grasslands, respectively.
            - The area calculations for each soil type are derived from the proportion of
            grassland area that is burnt and the share of each soil type within the
            grassland area.
        """

        ef_wildfire_MB_time_CF_mineral_soil_grassland = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_wildfire_GEF_ch4_mineral_soil_grassland"
            )
        )
        ef_wildfire_MB_time_CF_drained_organic_soil_grassland = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_wildfire_MB_time_CF_drained_organic_soil_grassland"
            )
        )
        ef_wildfire_MB_time_CF_wet_organic_soil_grassland = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_wildfire_MB_time_CF_wet_organic_soil_grassland"
            )
        )

        ef_wildfire_GEF_ch4_mineral = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_wildfire_GEF_ch4_mineral_soil_grassland"
            )
        )
        ef_wildfire_GEF_ch4_wet = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_wildfire_GEF_ch4_wet_in_organic_soil_grassland"
            )
        )
        ef_wildfire_GEF_ch4_drained = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_wildfire_GEF_ch4_drained_in_organic_grassland"
            )
        )

        fire_mineral_soil = (
            (
                self.land_use_data.grassland.area_ha
                * self.land_use_data.grassland.share_mineral
                * self.land_use_data.grassland.share_burnt
            )
            * ef_wildfire_MB_time_CF_mineral_soil_grassland
            * ef_wildfire_GEF_ch4_mineral
            * 10**-3
        )
        # fire_undrained_organic_soil = (
        # (
        # self.land_use_data.grassland.area_ha
        # * self.land_use_data.grassland.share_burnt
        # * (
        # self.land_use_data.grassland.share_organic
        # + self.land_use_data.grassland.share_organic_mineral
        # )
        # )
        # * ef_wildfire_MB_time_CF_wet_organic_soil_grassland
        # * ef_wildfire_GEF_ch4_wet
        # * 10**-3
        # )
        fire_drained_organic_soil = (
            (
                self.land_use_data.grassland.area_ha
                * self.land_use_data.grassland.share_burnt
                * self.land_use_data.grassland.share_organic
            )
            * ef_wildfire_MB_time_CF_drained_organic_soil_grassland
            * ef_wildfire_GEF_ch4_drained
            * 10**-3
        )

        return fire_mineral_soil + fire_drained_organic_soil

    def burning_n2o_grassland(self):
        """
        Calculates the nitrous oxide (N2O) emissions resulting from the burning of grasslands.
        This method assesses N2O emissions from two types of soil in grasslands: mineral soils
        and drained organic soils. The combustion factor (Cf) is assumed to be 1.0, signifying
        that all available fuel (biomass) is burned.

        Emission factors for N2O emissions are applied to both mineral and drained organic soils
        in grasslands. These factors are obtained from a country-specific database, reflecting
        regional variations in grassland composition and burning characteristics.

        The method involves calculating the N2O emissions by multiplying the area of grassland
        burned by the emission factors for N2O emissions from both soil types.

        Returns:
            float: The calculated N2O emissions (in tonnes) from the burning of grasslands,
                including both mineral soils and drained organic soils. The calculation
                involves considering the area of each soil type that is burned and their
                respective emission factors.

        Notes:
            - `ef_wildfire_GEF_n2o_grassland_mineral` and `ef_wildfire_GEF_n2o_grassland_drained` are the emission factors
            for N2O emissions from the burning of mineral soils and
            drained organic soils in grasslands, respectively.
            - The area calculations for each soil type are based on the proportion of grassland
            area that is burnt and the share of each soil type within the grassland area.
        """

        ef_wildfire_MB_time_CF_mineral_soil_grassland = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_wildfire_MB_time_CF_mineral_soil_grassland"
            )
        )
        ef_wildfire_MB_time_CF_drained_organic_soil_grassland = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_wildfire_MB_time_CF_drained_organic_soil_grassland"
            )
        )
        ef_wildfire_MB_time_CF_wet_organic_soil_grassland = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_wildfire_MB_time_CF_wet_organic_soil_grassland"
            )
        )

        ef_wildfire_GEF_n2o_grassland_mineral = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_wildfire_GEF_n2o_mineral_soil_grassland"
            )
        )
        ef_wildfire_GEF_n2o_grassland_wet = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_wildfire_GEF_n2o_wet_in_organic_grassland"
            )
        )
        ef_wildfire_GEF_n2o_grassland_drained = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_wildfire_GEF_n2o_drained_in_organic_grassland"
            )
        )

        fire_mineral_soil = (
            (
                self.land_use_data.grassland.area_ha
                * self.land_use_data.grassland.share_burnt
                * self.land_use_data.grassland.share_mineral
            )
            * ef_wildfire_MB_time_CF_mineral_soil_grassland
            * ef_wildfire_GEF_n2o_grassland_mineral
            * 10**-3
        )
        # fire_undrained_organic_soil = (
        # (
        # self.land_use_data.grassland.area_ha
        # * self.land_use_data.grassland.share_burnt
        # * (
        # self.land_use_data.grassland.share_organic
        # + self.land_use_data.grassland.share_organic_mineral
        # )
        # )
        # * ef_wildfire_MB_time_CF_wet_organic_soil_grassland
        # * ef_wildfire_GEF_n2o_grassland_wet
        # * 10**-3
        # )

        fire_drained_organic_soil = (
            (
                self.land_use_data.grassland.area_ha
                * self.land_use_data.grassland.share_burnt
                * self.land_use_data.grassland.share_organic
            )
            * ef_wildfire_MB_time_CF_drained_organic_soil_grassland
            * ef_wildfire_GEF_n2o_grassland_drained
            * 10**-3
        )

        return fire_mineral_soil + fire_drained_organic_soil


class Cropland(LandUse):
    """
    Represents a cropland land use.

    Args:
        ef_country (str): The country for which the emissions factors are calculated.
        transition_matrix_data (dict): The transition matrix data.
        land_use_data (dict): The land use data.
        past_land_use_data (dict): The past land use data.
        past_land_use (str, optional): The past land use. Defaults to None.
        current_land_use (str, optional): The current land use. Defaults to None.

    Attributes:
        current_land_use (str): The current land use, set to "cropland".
        current_area (float): The current area of cropland in hectares.
        current_area_drained (float): The current area of drained cropland in hectares.

    Methods:
        burning_ch4_cropland(): Calculates the CH4 emissions from burning cropland.
        burning_n2o_cropland(): Calculates the N2O emissions from burning cropland.
    """

    def __init__(
        self,
        ef_country,
        transition_matrix_data,
        land_use_data,
        past_land_use_data,
        past_land_use=None,
        current_land_use=None,
    ) -> None:
        super().__init__(
            ef_country,
            transition_matrix_data,
            land_use_data,
            past_land_use_data,
            past_land_use,
            current_land_use,
        )

        self.current_land_use = "cropland"
        self.current_area = self.land_use_data.cropland.area_ha
        self.current_area_drained = (
            self.land_use_data.cropland.area_ha
            * self.land_use_data.cropland.share_organic
        )

    def burning_ch4_cropland(self):
        """
        Calculates the methane (CH4) emissions resulting from the burning of cropland.
        This method assesses CH4 emissions specifically from cropland areas where
        crop residues and other biomass are burnt, a practice that can significantly
        contribute to CH4 emissions.

        The calculation involves two emission factors: one for the fuel burning in
        croplands (biomass combustion) and another emission factor (Gef) for
        CH4 emissions from cropland burning. These factors are sourced from a
        country-specific database, reflecting regional variations in agricultural
        practices and crop types.

        The total CH4 emissions are estimated by multiplying the current area of
        cropland that is burnt, the emission factors for fuel burning, and the
        general emission factor for CH4. The result is converted into tonnes for
        easier reporting and comparison.

        Returns:
            float: The calculated CH4 emissions (in tonnes) from the burning of
                cropland. The calculation considers the area of cropland burnt,
                the specific emission factor for fuel burning in croplands, and
                the general emission factor for CH4 emissions.

        Notes:
            - `ef_cropland_fuel_burning` refers to the emission factor for the burning
            of cropland fuels in terms of CH4.
            - `ef_ch4_cropland_Gef` is the general emission factor for CH4 emissions
            from cropland burning.
            - `self.current_area` represents the current area of cropland being analyzed.
            - `self.land_use_data.cropland.share_burnt` indicates the percentage of the
            cropland area that undergoes burning.
        """
        ef_cropland_fuel_burning = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_cropland_fuel_burning"
            )
        )
        ef_ch4_cropland_Gef = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_ch4_cropland_Gef"
            )
        )

        return (
            self.current_area
            * self.land_use_data.cropland.share_burnt
            * ef_cropland_fuel_burning
            * ef_ch4_cropland_Gef
            * 10**-3
        )

    def burning_n2o_cropland(self):
        """
        Calculates the nitrous oxide (N2O) emissions resulting from the burning of cropland.
        This method assesses N2O emissions specifically from cropland areas where crop
        residues and other biomass are burnt, a practice that can significantly contribute
        to N2O emissions.

        The calculation involves two emission factors: one for the fuel burning in croplands
        (biomass combustion) and another emission factor (Gef) for N2O emissions
        from cropland burning. These factors are sourced from a country-specific database,
        reflecting regional variations in agricultural practices and crop types.

        The total N2O emissions are estimated by multiplying the current area of cropland
        that is burnt, the emission factors for fuel burning, and the emission factor
        for N2O.

        Returns:
            float: The calculated N2O emissions (in tonnes) from the burning of cropland.
                The calculation considers the area of cropland burnt, the specific
                emission factor for fuel burning in croplands, and the general emission
                factor for N2O emissions.

        Notes:
            - `ef_cropland_fuel_burning` refers to the emission factor for the burning
            of cropland fuels in terms of N2O.
            - `ef_n2o_cropland_Gef` is the emission factor for N2O emissions
            from cropland burning.
            - `self.current_area` represents the current area of cropland being analyzed.
            - `self.land_use_data.cropland.share_burnt` indicates the percentage of the
            cropland area that undergoes burning.
        """
        ef_cropland_fuel_burning = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_cropland_fuel_burning"
            )
        )
        ef_n2o_cropland_Gef = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_n2o_cropland_Gef"
            )
        )

        return (
            self.current_area
            * self.land_use_data.cropland.share_burnt
            * ef_cropland_fuel_burning
            * ef_n2o_cropland_Gef
            * 10**-3
        )


class Forest(LandUse):
    """
    The Forest class is specifically tailored to handle calculations and assessments
    related to forest land use. It includes methods to estimate greenhouse gas emissions
    from various activities and conditions in forest ecosystems, such as drainage and burning.

    In addition to inheriting the functionalities of the LandUse class, the Forest
    class introduces specific attributes and methods to deal with forest-related
    data and emissions factors.

    Attributes:
        poor_drained_forest_area_exclude_over_50: The area of poorly drained forests
                                                  excluding those over 50 years old,
                                                  based on specific criteria.
        rich_drained_forest_area_exclude_over_50: The area of richly drained forests
                                                  excluding those over 50 years old,
                                                  based on specific criteria.
        forest_poor_drained_area: The total area of poorly drained forests.
        forest_rich_drained_area: The total area of richly drained forests.

    Methods:
        get_valid_area: Calculates the valid areas for poor and rich drained forests,
                        excluding forests over 50 years old.
        co2_drainage_organic_soils_forest: Estimates CO2 emissions from the drainage
                                           of organic soils in forest areas.
        ch4_drainage_organic_soils_forest: Estimates CH4 emissions from the drainage
                                           of organic soils in forest areas.
        n2o_drainage_organic_soils_forest: Estimates N2O emissions from the drainage
                                           of organic soils in forest areas.
        burning_co2_forest: Calculates CO2 emissions from the burning of forest areas.
        burning_ch4_forest: Calculates CH4 emissions from the burning of forest areas.
        burning_n2o_forest: Calculates N2O emissions from the burning of forest areas.
    """

    def __init__(
        self,
        ef_country,
        transition_matrix_data,
        land_use_data,
        past_land_use_data,
        past_land_use=None,
        current_land_use=None,
    ) -> None:
        super().__init__(
            ef_country,
            transition_matrix_data,
            land_use_data,
            past_land_use_data,
            past_land_use,
            current_land_use,
        )
        self.data_manager_class = DataManager()
        self.poor_drained_forest_area_exclude_over_50 = self.get_valid_area()[0]
        self.rich_drained_forest_area_exclude_over_50 = self.get_valid_area()[1]

        self.forest_poor_drained_area = (
            self.land_use_data.forest.area_ha * self.land_use_data.forest.share_organic
        )

        self.forest_rich_drained_area = (
            self.land_use_data.forest.area_ha
            * self.land_use_data.forest.share_organic_mineral
        )

    def get_valid_area(self):
        """
        Calculates the valid areas for poorly drained and richly drained forests,
        excluding forest areas that are over 50 years old. This method is crucial
        for determining the specific areas within forests that are relevant for
        certain environmental impact calculations, such as emissions from drainage
        or rewetting.

        The method first determines the proportion of forest area that is over 50
        years old and then calculates the remaining area (valid area) that is
        younger than 50 years. This valid area is then further divided into poorly
        drained and richly drained forest areas based on specific land use data.

        Returns:
            tuple: A tuple containing two values:
                - The first value is the valid area of poorly drained forests
                (considering only forests younger than 50 years).
                - The second value is the valid area of richly drained forests
                (considering only forests younger than 50 years).

        Notes:
            - The method uses 'forest_age_data' to determine the proportion of
            forest area over 50 years old.
            - 'land_use_data.forest.share_organic' and
            'land_use_data.forest.share_organic_mineral' are used to differentiate
            between poorly drained and richly drained forest areas.
        """
        over_50_years = self.forest_age_data.loc[
            (self.forest_age_data["year"] == 51), "aggregate"
        ].item()
        valid_area = 1 - over_50_years

        poor_forest_drained_area_valid = (
            self.land_use_data.forest.area_ha * valid_area
        ) * self.land_use_data.forest.share_organic

        rich_forest_drained_area_valid = (
            self.land_use_data.forest.area_ha * valid_area
        ) * self.land_use_data.forest.share_organic_mineral

        return poor_forest_drained_area_valid, rich_forest_drained_area_valid

    def co2_drainage_organic_soils_forest(self):
        """
        Estimates the carbon dioxide (CO2) emissions resulting from the drainage of organic
        soils in forest areas. This method considers both poorly and richly drained forest
        areas, excluding those over 50 years old, as it is assumed that areas older than
        50 years do not emit CO2 due to drainage.

        The calculation uses specific emission factors for both on-site and off-site drainage
        emissions. For richly drained forests, the emissions are adjusted based on the soil
        depth ratio to provide a more accurate estimation.

        Returns:
            float: The total CO2 emissions from the drainage of organic soils in forest areas.
                This includes emissions from both poorly and richly drained forests,
                excluding those over 50 years old.

        Notes:
            - `ef_co2_forest_drainage_off_site` and `ef_co2_forest_drainage_on_site` are
            the emission factors for off-site and on-site CO2 emissions, respectively,
            from forest drainage.
            - `soil_depth` represents the depth of the organic mineral soil, used to
            adjust the emission calculations for richly drained forests.
            - `self.poor_drained_forest_area_exclude_over_50` and
            `self.rich_drained_forest_area_exclude_over_50` represent the valid areas
            of poorly and richly drained forests that are younger than 50 years.
        """

        soil_depth = self.data_manager_class.organic_mineral_soil_depth

        SD_eq = soil_depth / 30

        ef_co2_forest_drainage_off_site = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_forest_drainage_off_site"
            )
        )
        ef_co2_forest_drainage_on_site = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_forest_drainage_on_site"
            )
        )

        co2_drainage_poor = (
            ef_co2_forest_drainage_on_site + ef_co2_forest_drainage_off_site
        ) * self.poor_drained_forest_area_exclude_over_50

        co2_drainage_rich = (
            self.rich_drained_forest_area_exclude_over_50
            * ef_co2_forest_drainage_on_site
            * SD_eq
        ) + (
            ef_co2_forest_drainage_off_site
            * self.rich_drained_forest_area_exclude_over_50
        )

        return co2_drainage_poor + co2_drainage_rich

    def ch4_drainage_organic_soils_forest(self):
        """
        Calculates methane (CH4) emissions resulting from the drainage of organic soils in
        forest areas. This method considers two types of drainage situations in forests:
        drainage on land and drainage through ditches, each with different emission factors.

        The method applies distinct emission factors for poorly and richly drained forests,
        taking into account the fraction of each forest type drained through ditches.
        This provides a more accurate estimation of CH4 emissions by considering the
        specific drainage practices employed in different forest areas.

        Returns:
            float: The total CH4 emissions from the drainage of organic soils in forest areas.
                This includes emissions from both poorly and richly drained forests,
                taking into account the respective proportions of drainage through ditches.

        Notes:
            - `ef_ch4_forest_drainage_land` refers to the emission factor for CH4 emissions
            from forest drainage on land.
            - `ef_ch4_forest_drainage_ditch` refers to the emission factor for CH4 emissions
            from forest drainage through ditches.
            - `frac_ditch_poor` and `frac_ditch_rich` represent the fractions of poorly and
            richly drained forest areas, respectively, that are drained through ditches.
            - `self.forest_poor_drained_area` and `self.forest_rich_drained_area` are the
            total areas of poorly and richly drained forests, respectively.
        """
        ef_ch4_forest_drainage_land = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_ch4_forest_drainage_land"
            )
        )
        ef_ch4_forest_drainage_ditch = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_ch4_forest_drainage_ditch"
            )
        )

        frac_ditch_poor = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "frac_ditch_poor"
            )
        )
        frac_ditch_rich = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "frac_ditch_rich"
            )
        )

        return (
            (
                ef_ch4_forest_drainage_land * (1.0 - (frac_ditch_poor))
                + (frac_ditch_poor) * ef_ch4_forest_drainage_ditch
            )
            * self.forest_poor_drained_area
        ) + (
            (
                ef_ch4_forest_drainage_land * (1.0 - (frac_ditch_rich))
                + (frac_ditch_rich) * ef_ch4_forest_drainage_ditch
            )
            * self.forest_rich_drained_area
        )

    def n2o_drainage_organic_soils_forest(self):
        """
        Calculates nitrous oxide (N2O) emissions resulting from the drainage of organic
        soils in forest areas. This method separately considers the emissions from poorly
        and richly drained forests, each with their specific emission factors.

        The calculation involves applying distinct emission factors for N2O emissions for
        both poorly and richly drained forests. This approach ensures a more accurate
        estimation of N2O emissions by considering the specific drainage characteristics
        and soil conditions of different forest types.

        Returns:
            float: The total N2O emissions from the drainage of organic soils in forest areas.
                This includes emissions from both poorly and richly drained forests,
                calculated using the respective emission factors for each forest type.

        Notes:
            - `ef_n2o_forest_drainage_rich` refers to the emission factor for N2O emissions
            from the drainage of organic soils in richly drained forests.
            - `ef_n2o_forest_drainage_poor` refers to the emission factor for N2O emissions
            from the drainage of organic soils in poorly drained forests.
            - `self.forest_rich_drained_area` and `self.forest_poor_drained_area` represent
            the total areas of richly and poorly drained forests, respectively.
        """
        ef_n2o_forest_drainage_rich = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_n2o_forest_drainage_rich"
            )
        )
        ef_n2o_forest_drainage_poor = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_n2o_forest_drainage_poor"
            )
        )

        return (self.forest_rich_drained_area * ef_n2o_forest_drainage_rich) + (
            self.forest_poor_drained_area * ef_n2o_forest_drainage_poor
        )

    def burning_co2_forest(self):
        """
        Calculates carbon dioxide (CO2) emissions resulting from the burning of forests.
        This method assesses CO2 emissions specifically from forest areas where vegetation
        and other biomass are burnt, a practice that can significantly contribute to CO2 emissions.

        The calculation involves multiple factors: an emission factor for the fuel burning in
        forests, a emission factor (Gef) for CO2 emissions from forest burning, and a
        combustion factor (Cf) that represents the efficiency of biomass combustion.

        The total CO2 emissions are estimated by multiplying the area of forest burnt, the
        emission factor for fuel burning, the combustion factor, and the emission factor
        for CO2. The result is then converted into tonnes for easier reporting and comparison.

        Returns:
            float: The calculated CO2 emissions (in tonnes) from the burning of forest areas.
                The calculation considers the area of forest burnt, the specific emission
                factor for fuel burning in forests, the combustion factor, and the
                emission factor for CO2 emissions.

        Notes:
            - `ef_forest_fuel_burning` refers to the emission factor for the burning of
            forest fuels in terms of CO2.
            - `ef_co2_forest_Gef` is the emission factor for CO2 emissions from
            forest burning.
            - `combustion_factor` (ef_forest_Cf) indicates the efficiency of biomass
            combustion in the forest.
            - `self.land_use_data.forest.area_ha` represents the total area of forests
            being analyzed.
            - `self.land_use_data.forest.share_burnt` indicates the percentage of the
            forest area that undergoes burning.
        """
        ef_forest_fuel_burning = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_forest_fuel_burning"
            )
        )
        ef_co2_forest_Gef = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_forest_Gef"
            )
        )

        combustion_factor = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_forest_Cf"
            )
        )

        return (
            (self.land_use_data.forest.area_ha * self.land_use_data.forest.share_burnt)
            * ef_forest_fuel_burning
            * combustion_factor
            * ef_co2_forest_Gef
            * 10**-3
        )

    def burning_ch4_forest(self):
        """
        Calculates methane (CH4) emissions resulting from the burning of forests. This method
        assesses CH4 emissions specifically from forest areas where vegetation and other
        biomass are burnt, which can be a significant source of methane, a potent greenhouse gas.

        The calculation involves several factors: an emission factor for the fuel burning in
        forests, a emission factor (Gef) for CH4 emissions from forest burning, and a
        combustion factor (Cf) that represents the efficiency of biomass combustion.

        The total CH4 emissions are estimated by multiplying the area of forest burnt, the
        emission factor for fuel burning, the combustion factor, and the emission factor
        for CH4. The result is then converted into tonnes for easier reporting and comparison.

        Returns:
            float: The calculated CH4 emissions (in tonnes) from the burning of forest areas.
                The calculation considers the area of forest burnt, the specific emission
                factor for fuel burning in forests, the combustion factor, and the
                emission factor for CH4 emissions.

        Notes:
            - `ef_forest_fuel_burning` refers to the emission factor for the burning of
            forest fuels in terms of CH4.
            - `ef_ch4_forest_Gef` is the emission factor for CH4 emissions from
            forest burning.
            - `combustion_factor` (ef_forest_Cf) indicates the efficiency of biomass
            combustion in the forest.
            - `self.land_use_data.forest.area_ha` represents the total area of forests
            being analyzed.
            - `self.land_use_data.forest.share_burnt` indicates the percentage of the
            forest area that undergoes burning.
        """
        ef_forest_fuel_burning = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_forest_fuel_burning"
            )
        )
        ef_ch4_forest_Gef = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_ch4_forest_Gef"
            )
        )

        combustion_factor = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_forest_Cf"
            )
        )

        return (
            (self.land_use_data.forest.area_ha * self.land_use_data.forest.share_burnt)
            * ef_forest_fuel_burning
            * combustion_factor
            * ef_ch4_forest_Gef
            * 10**-3
        )

    def burning_n2o_forest(self):
        """
        Calculates nitrous oxide (N2O) emissions resulting from the burning of forests.
        This method assesses N2O emissions specifically from forest areas where vegetation
        and other biomass are burnt. N2O is a potent greenhouse gas, and its emissions
        can be significant in forest burning events.

        The calculation involves several factors: an emission factor for the fuel burning
        in forests, a emission factor (Gef) for N2O emissions from forest burning,
        and a combustion factor (Cf) that represents the efficiency of biomass combustion.

        The total N2O emissions are estimated by multiplying the area of forest burnt, the
        emission factor for fuel burning, the combustion factor, and the emission
        factor for N2O. The result is then converted into tonnes for easier reporting and
        comparison.

        Returns:
            float: The calculated N2O emissions (in tonnes) from the burning of forest areas.
                The calculation considers the area of forest burnt, the specific emission
                factor for fuel burning in forests, the combustion factor, and the
                emission factor for N2O emissions.

        Notes:
            - `ef_forest_fuel_burning` refers to the emission factor for the burning of
            forest fuels in terms of N2O.
            - `ef_n2o_forest_Gef` is the emission factor for N2O emissions from
            forest burning.
            - `combustion_factor` (ef_forest_Cf) indicates the efficiency of biomass
            combustion in the forest.
            - `self.land_use_data.forest.area_ha` represents the total area of forests
            being analyzed.
            - `self.land_use_data.forest.share_burnt` indicates the percentage of the
            forest area that undergoes burning.
        """
        ef_forest_fuel_burning = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_forest_fuel_burning"
            )
        )
        ef_n2o_forest_Gef = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_n2o_forest_Gef"
            )
        )

        combustion_factor = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_forest_Cf"
            )
        )

        return (
            (self.land_use_data.forest.area_ha * self.land_use_data.forest.share_burnt)
            * ef_forest_fuel_burning
            * combustion_factor
            * ef_n2o_forest_Gef
            * 10**-3
        )

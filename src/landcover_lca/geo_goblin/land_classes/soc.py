import numpy as np
from landcover_lca.resource_manager.data_loader import Loader
from landcover_lca.geo_goblin.geo_models import Emissions_Factors, Land_Use_Features
from landcover_lca.resource_manager.landcover_data_manager import DataManager


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
            - ef_country (str): The country for which the land use data is being analyzed.
            - land_use_data: Land use transition data for future scenarios.
            - past_land_use_data: Data representing current or past land use scenarios.
            - transition_matrix_data (TransitionMatrixData): An instance of TransitionMatrixData
                class containing data for transitions between different land use categories over time.
            - current_land_use (str): The current/future land use category.
            - past_land_use (str): The past land use category.

        Attributes:
            - data_loader_class (Loader): An instance of the Loader class for loading
                country-specific data.
            - ipcc_soil_class_SOC (DataFrame): The IPCC soil class SOC factors
                for different soil types.
            - land_use_data: Land use transition data for future scenarios.
            - past_land_use_data: Data representing current or past land use scenarios.
            - transition_matrix_data (TransitionMatrixData): An instance of TransitionMatrixData
                class containing data for transitions between different land use categories over time.
            - land_use_features (Land_Use_Features): An instance of the Land_Use_Features class
                for extracting land use features.
            - current_land_use (str): The current/future land use category.
            - past_land_use (str): The past land use category.
            - year_range (int): The time period between the current and past land use data.

        Methods:
            - get_time_period: Calculates the time period between the current and past land use data.
            - compute_SOC_ref_for_land_use: Computes the reference SOC for the current land use category.
            - compute_land_use_change_total_area: Computes the total area converted from the past land use
                to the current land use.
            - compute_emission_factor_from_mineral_soils: Computes the emission factor from mineral soils
                for a given land use category.
            - compute_emissions_from_mineral_soils_in_land_use_change: Computes the emissions from mineral
                soils during land use change.
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
                        * (EF_SOC_previous_land_use - EF_SOC_current_land_use)
                    ) / transition_period
                else:
                    return soc
        else:
            return soc

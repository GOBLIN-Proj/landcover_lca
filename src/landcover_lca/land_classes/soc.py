import numpy as np
from landcover_lca.resource_manager.data_loader import Loader
from landcover_lca.models import (
    Emissions_Factors,
    Land_Use_Features,
    get_transition_area,
)
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
        Computes the reference SOC (t C/ha) used for this transition.

        - Any transition involving cropland (cropland as the past or the current land
          use) uses the Low Activity Clay (LAC) value, 85 t C/ha. NID 2026 s.6.4.6:
          98% of cropland is on LAC soils and only grassland on LAC soils converts
          directly to cropland. With the Table 6.31 adjustment factors this
          reproduces Table 6.32 (58.7 = 85 x 0.69; 69.7 = 85 x 0.82).
        - Every other transition uses the area-weighted mean of the four soil classes
          (73.51 t C/ha; the proportions sum to 0.83 and are not renormalised).
          Forest to grassland is a known simplification (D4b): the NID inventories it
          with Tier 2 soil-group values (Tables 6.20, 6.21): the 2026 CRT shows an emission
          of +17.9 t C/ha over 20 years against a removal of -7.35 here (opposite sign). It is left as is because landcover_assignment
          never creates forest transitions, so GOBLIN never reaches it. Grassland to forest
          (afforestation) is the transition that occurs, and CBM covers forests.

        Returns:
            float: The reference SOC value in t C/ha.
        """
        soil = self.ipcc_soil_class_SOC
        if "cropland" in (self.past_land_use, self.current_land_use):
            lac = soil.loc[soil["IPCCSoilClass"] == "LAC", "SOCref"]
            return float(lac.iloc[0])
        return np.sum(soil["Proportion"] * soil["SOCref"])

    def compute_land_use_change_total_area(self):
        """
        Computes the total area converted from the past land use to the current land use.

        Returns:
            float: The annual area converted.
        """
        land_use_total_area = get_transition_area(
            self.transition_matrix_data, self.past_land_use, self.current_land_use
        )

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

        NID 2026 eq 6.4.3: each converted hectare loses (SOC_past - SOC_current) / 20
        per year for 20 years. Positive = emission, negative = removal.

        This is a snapshot at one year, not a time series. ``year_range`` is the
        elapsed time from the past (baseline) year to the evaluated year, so it is the
        position in time: 15 means "15 years after the baseline". To evaluate another
        year, call with that year's land use data.

        The converted area is assumed to convert in equal annual slices (cohorts):
        ``annual_area = total / year_range``, because the transition matrix only gives a
        total for the period, not the year each hectare converted. At the evaluated year
        a cohort is still releasing carbon if it was converted fewer than 20 years ago,
        so ``min(year_range, 20)`` cohorts contribute.
            - Span of 20 years or less: every cohort is still releasing, and the result
              does not depend on the timing of conversion.
            - Span over 20 years: the earliest cohorts have finished, and the result
              does depend on the even-split assumption. For 1,000 ha over 30 years,
              the same total gives 1,102.65 (even split), 1,653.97 (all converted in
              the last 5 years) or 0 (all converted in the first 5 years), in
              t C/yr for a delta SOC of 33.08 t C/ha.

        Returns:
            float: Emission rate in the evaluated year in **t C per year** (positive =
            emission). The lca_emission CO2 functions convert this to kg CO2 (x 1000 x 44/12).
            Raises ValueError if year_range < 0.

        Assumptions (see README, section "Soil organic carbon"):
            - SOC = SOCref x adjustment factor. SOCref is LAC (85 t C/ha) for any
              transition involving cropland, otherwise the area-weighted mean over the
              four mineral soil classes (see compute_SOC_ref_for_land_use).
            - Every "grassland" conversion uses the database row "grassland", adjustment
              factor 1.14 (NID Table 6.31 improved grassland). There is no improved /
              unimproved split.
        """
        EF_SOC_previous_land_use = self.compute_emission_factor_from_mineral_soils(
            self.past_land_use
        )

        EF_SOC_current_land_use = self.compute_emission_factor_from_mineral_soils(
            self.current_land_use
        )

        if self.year_range < 0:
            raise ValueError(
                f"year_range is negative ({self.year_range}): the current land use "
                "year is earlier than the past land use year."
            )

        annual_area = self.compute_land_use_change_total_area()

        # NID 2026 eq 6.4.3 (IPCC eq 2.25): each converted hectare loses
        # (SOC_past - SOC_current) / T per year for T = 20 years. Positive = emission.
        # The result is the emission rate in the target year. Cohorts converted more
        # than 20 years before the target have finished emitting, so at most 20
        # annual cohorts contribute.
        transition_period = 20

        if not annual_area:
            return 0

        return (
            annual_area
            * min(self.year_range, transition_period)
            * (EF_SOC_previous_land_use - EF_SOC_current_land_use)
            / transition_period
        )

import numpy as np
from landcover_lca.resource_manager.data_loader import Loader
from landcover_lca.models import Emissions_Factors


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
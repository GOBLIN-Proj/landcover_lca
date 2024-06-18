from landcover_lca.geo_goblin.land_classes.landuse import LandUse

class Cropland(LandUse):
    """
    Represents a cropland land use.

    Args:
        - ef_country (str): The country for which the land use data is being analyzed.
        - transition_matrix_data (TransitionMatrixData): An instance of TransitionMatrixData
            class containing data for transitions between different land use categories over time.
        - land_use_data: Land use transition data for future scenarios.
        - past_land_use_data: Data representing current or past land use scenarios.
        - past_land_use (str, optional): The past land use category. Defaults to None.
        - current_land_use (str, optional): The current/future land use category. Defaults to None.


    Attributes:
        - current_land_use (str): The current/future land use category.
        - current_area (float): The current area of cropland.
        - current_area_drained (float): The current area of cropland that is drained.


    Methods:
        - burning_ch4_cropland: Calculates the methane (CH4) emissions resulting from the
            burning of cropland.
        - burning_n2o_cropland: Calculates the nitrous oxide (N2O) emissions resulting from
            the burning of cropland.
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
                "ef_wildfire_MB_time_CF_cropland"
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
                "ef_wildfire_MB_time_CF_cropland"
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

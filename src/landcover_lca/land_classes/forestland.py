from landcover_lca.land_classes.landuse import LandUse
from landcover_lca.resource_manager.landcover_data_manager import DataManager

class Forest(LandUse):
    """
    The Forest class is specifically tailored to handle calculations and assessments
    related to forest land use. It includes methods to estimate greenhouse gas emissions
    from various activities and conditions in forest ecosystems, such as drainage and burning.

    In addition to inheriting the functionalities of the LandUse class, the Forest
    class introduces specific attributes and methods to deal with forest-related
    data and emissions factors.

    Attributes:
        - poor_drained_forest_area_exclude_over_50 (float): The valid area of poorly drained
                                                              forests younger than 50 years.        
        - rich_drained_forest_area_exclude_over_50 (float): The valid area of richly drained
                                                                forests younger than 50 years.
        - forest_poor_drained_area (float): The total area of poorly drained forests.
        - forest_rich_drained_area (float): The total area of richly drained forests.


    Methods:
        - get_valid_area(): Calculates the valid areas for poorly and richly drained forests,
                            excluding forest areas that are over 50 years old.

        - co2_drainage_organic_soils_forest(): Estimates CO2 emissions from the drainage of
                                                organic soils in forest areas.  

        - ch4_drainage_organic_soils_forest(): Calculates CH4 emissions from the drainage of
                                                organic soils in forest areas.

        - n2o_drainage_organic_soils_forest(): Calculates N2O emissions from the drainage of
                                                organic soils in forest areas.  

        - burning_co2_forest(): Calculates CO2 emissions from the burning of forest areas.

        - burning_ch4_forest(): Calculates CH4 emissions from the burning of forest areas.

        - burning_n2o_forest(): Calculates N2O emissions from the burning of forest areas.

    Args:
        - ef_country (str): The country for which the emissions factors are calculated.
        - transition_matrix_data (dict): The transition matrix data.
        - land_use_data (dict): The land use data.
        - past_land_use_data (dict): The past land use data.
        - past_land_use (str, optional): The past land use. Defaults to None.
        - current_land_use (str, optional): The current land use. Defaults to None.

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

        soil_depth = self.data_manager_class.get_organic_mineral_soil_depth()

        SD_eq = soil_depth / 30

        ef_co2_forest_drainage_off_site = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_forest_drainage_off_site_DOC"
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
            float: The total CH4 emissions in kg from the drainage of organic soils in forest areas.
                This includes emissions from both poorly and richly drained forests,
                taking into account the respective proportions of drainage through ditches.

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
            float: The total N2O emissions in kg from the drainage of organic soils in forest areas.
                This includes emissions from both poorly and richly drained forests,
                calculated using the respective emission factors for each forest type.

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
        Carbon dioxide (CO2) from forest wildfires, in tonnes.

        Burnt area (forest area_ha x share_burnt) x the implied factor ef_co2_implied_wildfire_forest
        (kg CO2 per ha burnt) x 1e-3. The factor is the 2020-2022 inventory value: CRT 2026 Table 4(IV)
        4.A.1 + 4.A.2 emissions / CRF 2024 area burnt (FIRE-1, docs/emission_factor_provenance.md). It is a
        total-forest factor, so share_burnt should be the total forest burnt area (forest remaining forest plus
        land converted to forest).

        Returns:
            float: CO2 emissions from forest wildfires (t).
        """
        ef_co2_forest = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_implied_wildfire_forest"
            ) * 1e-3
        )


        return (
            (self.land_use_data.forest.area_ha * self.land_use_data.forest.share_burnt)
            * ef_co2_forest
        )

    def burning_ch4_forest(self):
        """
        Methane (CH4) from forest wildfires, in tonnes.

        Burnt area (forest area_ha x share_burnt) x the implied factor ef_ch4_implied_wildfire_forest
        (kg CH4 per ha burnt) x 1e-3. The factor is the 2020-2022 inventory value: CRT 2026 Table 4(IV)
        4.A.1 + 4.A.2 emissions / CRF 2024 area burnt (FIRE-1, docs/emission_factor_provenance.md). It is a
        total-forest factor, so share_burnt should be the total forest burnt area (forest remaining forest plus
        land converted to forest).

        Returns:
            float: CH4 emissions from forest wildfires (t).
        """
        ef_ch4_forest = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_ch4_implied_wildfire_forest"
            ) * 1e-3
        )

        return (
            (self.land_use_data.forest.area_ha * self.land_use_data.forest.share_burnt)
            * ef_ch4_forest
        )

    def burning_n2o_forest(self):
        """
        Nitrous oxide (N2O) from forest wildfires, in tonnes.

        Burnt area (forest area_ha x share_burnt) x the implied factor ef_n2o_implied_wildfire_forest
        (kg N2O per ha burnt) x 1e-3. The factor is the 2020-2022 inventory value: CRT 2026 Table 4(IV)
        4.A.1 + 4.A.2 emissions / CRF 2024 area burnt (FIRE-1, docs/emission_factor_provenance.md). It is a
        total-forest factor, so share_burnt should be the total forest burnt area (forest remaining forest plus
        land converted to forest).

        Returns:
            float: N2O emissions from forest wildfires (t).
        """
        ef_n2o_forest = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_n2o_implied_wildfire_forest"
            ) * 1e-3
        )

        return (
            (self.land_use_data.forest.area_ha * self.land_use_data.forest.share_burnt)
            * ef_n2o_forest
        )

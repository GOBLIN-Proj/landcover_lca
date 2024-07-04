from landcover_lca.geo_goblin.land_classes.landuse import LandUse
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
        - afforested_area (float): The total area of afforested forest land.
        - legacy_area (float): The total area of legacy forest land.



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

        - total_N_exports_to_water(): Calculates the total nitrogen exports to water bodies

        - N_exports_to_water_legacy_forest(): Estimates nitrogen exports to water bodies

        - N_exports_to_water_afforested_forest(): Estimates nitrogen exports to water bodies

        - total_P_exports_to_water(): Calculates the total phosphorus exports to water bodies

        - P_exports_to_water_legacy_forest(): Estimates phosphorus exports to water bodies

        - P_exports_to_water_afforested_forest(): Estimates phosphorus exports to water bodies

        - total_PO4e_exports_to_water(): Calculates the total phosphorus equivalent exports to water bodies

        - total_N_exports_to_water_as_po4e(): Calculates the total nitrogen equivalent exports to water bodies

        - total_P_exports_to_water_as_po4e(): Calculates the total phosphorus equivalent exports to water bodies

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

        self.afforested_area = self.get_total_grassland_transition_area()

        self.legacy_area = self.land_use_data.forest.area_ha - self.afforested_area


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

        """
        ef_co2_forest = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_implied_wilfire_forest"
            ) * 1e-3
        )


        return (
            (self.land_use_data.forest.area_ha * self.land_use_data.forest.share_burnt)
            * ef_co2_forest
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
        """
        ef_ch4_forest = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_CH4_implied_wilfire_forest"
            ) * 1e-3
        )

        return (
            (self.land_use_data.forest.area_ha * self.land_use_data.forest.share_burnt)
            * ef_ch4_forest
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

        """
        ef_n2o_forest = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_n2o_implied_wilfire_forest"
            ) * 1e-3
        )

        return (
            (self.land_use_data.forest.area_ha * self.land_use_data.forest.share_burnt)
            * ef_n2o_forest
        )
    
    def total_N_exports_to_water(self):
        """
        Calculates the total nitrogen (N) exports to water bodies from forest areas.

        The method estimates the N exports to water by summing the N exports from both
        legacy forest areas and afforested forest areas.

        Returns:
            float: The total N exports to water bodies from forest areas.
        """
        return self.N_exports_to_water_legacy_forest() + self.N_exports_to_water_afforested_forest()


    def N_exports_to_water_legacy_forest(self):
        """
        Estimates the nitrogen (N) exports to water bodies from legacy forest areas.

        The calculation involves multiplying the area of legacy forest by the N export
        factor for default forest conditions. This provides an estimate of the total N
        exports to water from legacy forest areas.

        Returns:
            float: The N exports to water bodies from legacy forest areas.
        """
        n_export_kg_per_ha = self.nutrient_export_factors.get_N_export_factor_in_export_factor_data_base("forest","default")

        return self.legacy_area * n_export_kg_per_ha
    

    def N_exports_to_water_afforested_forest(self):
        """
        Estimates the nitrogen (N) exports to water bodies from afforested forest areas.

        The calculation involves multiplying the area of afforested forest by the N export
        factor for transitional forest conditions. This provides an estimate of the total N
        exports to water from afforested forest areas.

        Returns:
            float: The N exports to water bodies from afforested forest areas.
        """
        n_export_kg_per_ha = self.nutrient_export_factors.get_N_export_factor_in_export_factor_data_base("forest","transitional")

        return self.afforested_area * n_export_kg_per_ha
    

    def total_P_exports_to_water(self):
        """
        Calculates the total phosphorus (P) exports to water bodies from forest areas.

        The method estimates the P exports to water by summing the P exports from both
        legacy forest areas and afforested forest areas.

        Returns:
            float: The total P exports to water bodies from forest areas.
        """ 
        return self.P_exports_to_water_legacy_forest() + self.P_exports_to_water_afforested_forest()
    

    def P_exports_to_water_legacy_forest(self):
        """
        Estimates the phosphorus (P) exports to water bodies from legacy forest areas.

        The calculation involves multiplying the area of legacy forest by the P export
        factor for default forest conditions. This provides an estimate of the total P
        exports to water from legacy forest areas.

        Returns:
            float: The P exports to water bodies from legacy forest areas.
        """

        p_export_kg_per_ha = self.nutrient_export_factors.get_P_export_factor_in_export_factor_data_base("forest","default")

        return self.legacy_area * p_export_kg_per_ha
    
    def P_exports_to_water_afforested_forest(self):
        """
        Estimates the phosphorus (P) exports to water bodies from afforested forest areas.

        The calculation involves multiplying the area of afforested forest by the P export
        factor for transitional forest conditions. This provides an estimate of the total P
        exports to water from afforested forest areas.

        Returns:
            float: The P exports to water bodies from afforested forest areas.
        """
        p_export_kg_per_ha = self.nutrient_export_factors.get_P_export_factor_in_export_factor_data_base("forest","transitional")

        return self.afforested_area * p_export_kg_per_ha
    
    def total_PO4e_exports_to_water(self):
        """
        Calculates the total phosphorus equivalent (PO4e) exports to water bodies from forest areas.

        The method estimates the PO4e exports to water by summing the PO4e exports from both
        legacy forest areas and afforested forest areas.

        Returns:
            float: The total PO4e exports to water bodies from forest areas.
        """
        return self.total_N_exports_to_water_as_po4e() + self.total_P_exports_to_water_as_po4e()
    
    def total_N_exports_to_water_as_po4e(self):
        """
        Calculates the total nitrogen equivalent (N) exports to water bodies from forest areas.

        The method estimates the N exports to water by summing the N exports from both
        legacy forest areas and afforested forest areas, and converting the total N
        exports to phosphate equivalent (PO4e).

        Returns:
            float: The total N exports to water bodies from forest areas, converted to PO4e.
        """
        return self.total_N_exports_to_water() * self.data_manager_class.get_total_N_to_po4e()
    

    def total_P_exports_to_water_as_po4e(self):
        """
        Calculates the total phosphorus equivalent (P) exports to water bodies from forest areas.

        The method estimates the P exports to water by summing the P exports from both
        legacy forest areas and afforested forest areas, and converting the total P
        exports to phosphate equivalent (PO4e).

        Returns:
            float: The total P exports to water bodies from forest areas, converted to PO4e.
        """
        return self.total_P_exports_to_water() * self.data_manager_class.get_total_P_to_po4e()

    

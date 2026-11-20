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
        - forest_poor_drained_area (float): Drained organic (N-poor) forest area, ha (area x share_organic).
        - forest_rich_drained_area (float): Drained organo-mineral (N-rich) forest area, ha
                                            (area x share_organic_mineral). CO2, CH4 and N2O all use these.
        - afforested_area (float): The total area of afforested forest land.
        - legacy_area (float): The total area of legacy forest land.



    Methods:
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

        self.forest_poor_drained_area = (
            self.land_use_data.forest.area_ha * self.land_use_data.forest.share_organic
        )

        self.forest_rich_drained_area = (
            self.land_use_data.forest.area_ha
            * self.land_use_data.forest.share_organic_mineral
        )

        self.afforested_area = self.get_total_grassland_transition_area()

        self.legacy_area = self.land_use_data.forest.area_ha - self.afforested_area


    def co2_drainage_organic_soils_forest(self):
        """
        CO2 from drained organic and organo-mineral forest soils, as NID 2026 s.6.3 (eq 6.3.2-6.3.4, p.215-216).

            CO2 = A_organic x (EF_on-site + EF_DOC) + A_organo-mineral x (EF_on-site x SD + EF_DOC)

        - A_organic = area x share_organic (drained N-poor); A_organo-mineral = area x share_organic_mineral
          (drained N-rich). The same areas as the CH4 and N2O methods. No age cut-off: the NID applies the factors
          "to all forest over the entire time series regardless of forest age" (p.216). Open areas (roads,
          extraction routes) are not drained; the input areas should exclude them, as NID Tables 6.7 and 6.15 do.
        - EF_on-site = 1.68 t C/ha/yr (``ef_co2_forest_drainage_on_site``, eq 6.3.2); EF_DOC = 0.31 t C/ha/yr
          (``ef_co2_forest_drainage_off_site_DOC``), both as kg CO2/ha after units.py.
        - SD = 0.581 (``sd_forest_organo_mineral``): depth / 30 cm for organo-mineral soils (eq 6.3.3-6.3.4). The
          NID text gives no depth; its Tables 6.7 and 6.15 do: organo-mineral on-site / (area x 1.68), 4.A.1 and
          4.A.2 pooled, 2020-2023 = 381.0 kt C / (390.5 kha x 1.68) = 0.5808 (17.4 cm).

        Example: 1,000 ha organic and 500 ha organo-mineral give 1,000 x (1.68 + 0.31) + 500 x (1.68 x 0.581 + 0.31)
        = 1,990.0 + 643.04 = 2,633.04 t C = 9,654,480 kg CO2 (x 1000 x 44/12). With the NID 2020-2023 areas this reproduces the CRT 4.A organic-soil carbon
        (package/CRT 0.9998-1.0001). Before F6 the package removed forest over 50 years old
        (8.1%) from this area only and used a depth of 28 cm (SD 0.933); the two nearly cancelled.

        Returns:
            float: CO2 from drained forest soils, kg CO2 per year.
        """
        get = self.emissions_factors.get_emission_factor_in_emission_factor_data_base
        ef_on_site = get("ef_co2_forest_drainage_on_site")
        ef_doc = get("ef_co2_forest_drainage_off_site_DOC")
        sd = get("sd_forest_organo_mineral")

        co2_organic = self.forest_poor_drained_area * (ef_on_site + ef_doc)
        co2_organo_mineral = self.forest_rich_drained_area * (ef_on_site * sd + ef_doc)
        return co2_organic + co2_organo_mineral

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

    

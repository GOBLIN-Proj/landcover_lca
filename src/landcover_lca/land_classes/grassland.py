from landcover_lca.land_classes.landuse import LandUse

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
        - mineral_co2_in_grassland(): Calculate the CO2 emissions from mineral soils in grassland.
        - drainage_co2_organic_soils_in_grassland(): Calculate the CO2 emissions from the drainage of organic soils in grassland.
        - drainage_ch4_organic_soils_in_grassland(): Calculate the CH4 emissions from the drainage of organic soils in grassland.
        - drainage_n2O_organic_soils_in_grassland(): Calculate the N2O emissions from the drainage of organic soils in grassland.
        - rewetting_co2_organic_soils_in_grassland(): Calculate the CO2 emissions from the rewetting of organic soils in grassland.
        - rewetting_ch4_organic_soils_in_grassland(): Calculate the CH4 emissions from the rewetting of organic soils in grassland.
        - burning_co2_grassland(): Calculate the CO2 emissions from the burning of grassland.
        - burning_ch4_grassland(): Calculate the CH4 emissions from the burning of grassland.
        - burning_n2o_grassland(): Calculate the N2O emissions from the burning of grassland.

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

        self.current_area_mineral = (
            self.land_use_data.grassland.area_ha
            * self.land_use_data.grassland.share_mineral
        )

        self.current_area_drained_rich = (
            self.land_use_data.grassland.area_ha
            * self.land_use_data.grassland.share_drained_rich_organic
        )

        self.current_area_drained_poor = (
            self.land_use_data.grassland.area_ha
            * self.land_use_data.grassland.share_drained_poor_organic
        )

        self.current_area_rewetted_poor = (
            self.land_use_data.grassland.area_ha
            * self.land_use_data.grassland.share_rewetted_poor_organic
        )

        self.current_area_rewetted_rich = (
            self.land_use_data.grassland.area_ha
            * self.land_use_data.grassland.share_rewetted_rich_organic
        )

    def mineral_co2_in_grassland(self):
        """
        Calculate the CO2 removals from mineral soils in grassland. This uses and implied 
        emission factor based on Ireland's national inventory reporting.

        Returns:
            float: The CO2 removals in kg from mineral soils in grassland.
        """
        ef_co2_mineral_soils = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_implied_grassland_remaining_SOC_per_ha"
            )
        )

        return self.current_area_mineral * ef_co2_mineral_soils


    def drainage_co2_organic_soils_in_grassland(self):
        """
        Calculates the carbon dioxide (CO2) onsite and offsite emissions resulting from the drainage of organic
        soils in grassland areas. Draining organic soils can lead to significant CO2 emissions.
        This process exposes previously waterlogged organic matter to oxygen, accelerating its
        decomposition and releasing stored carbon into the atmosphere.

        This method focuses specifically on CO2 emissions from on-site sources in grasslands
        where organic soils have been drained. The emission factor used for this calculation
        is tailored to the specific conditions of drained grasslands, reflecting the typical
        rate of CO2 emissions per unit area for such land use change.

        The emission factors are obtained from a country-specific database of emission factors,
        ensuring the calculation is representative of regional characteristics and land
        management practices.

        Returns:
            float: The calculated CO2 emissions in kg resulting from the drainage of organic soils
                in grassland areas. The emissions are based on the current area of drained
                land and the specific emission factor for CO2 emissions from grassland drainage.
        """
        onsite_emissions = self.drainage_onsite_co2_organic_soils_in_grassland()
        offsite_emissions = self.drainage_offsite_co2_organic_soils_in_grassland()

        return onsite_emissions + offsite_emissions
    
    
    def drainage_onsite_co2_organic_soils_in_grassland(self):
        """
        Calculates the carbon dioxide (CO2) emissions resulting from the drainage of poor and rich organic
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
            float: The calculated CO2 emissions in kg resulting from the drainage of poor and rich organic soils
                in grassland areas. The emissions are based on the current area of drained
                land and the specific emission factor for CO2 emissions from grassland drainage.
        """

        ef_co2_grassland_drainage_on_site_poor = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_grassland_drainage_on_site_poor"
            )
        )

        ef_co2_grassland_drainage_on_site_rich = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_grassland_drainage_on_site_rich"
            )
        )

        emissions_poor = self.current_area_drained_poor * ef_co2_grassland_drainage_on_site_poor
        emissions_rich = self.current_area_drained_rich * ef_co2_grassland_drainage_on_site_rich

        return emissions_poor + emissions_rich
    
    def drainage_offsite_co2_organic_soils_in_grassland(self):
        """
        Cacluates the offsite CO2 emissions, in the form of Disolved Organic Carbon (DOC) from the drainage of poor and rich organic
        soils in grassland areas.

        A tier 1 approach is used to estimate the DOC emissions from the drained organic soils in grasslands.

        Returns:
            float: The calculated CO2 emissions in kg resulting from the drainage of poor and rich organic soils
                in grassland areas. The emissions are based on the current area of drained
                land and the specific emission factor for CO2 emissions from grassland drainage.
        """

        ef_co2_offsite_grassland_draingage_DOC= (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_grassland_drainage_off_site"
            )
        )

        return (self.current_area_drained_poor + self.current_area_drained_rich)* ef_co2_offsite_grassland_draingage_DOC


    def drainage_ch4_organic_soils_in_grassland(self):
        """
        Calculates the methane (CH4) emissions resulting from the drainage of poor and rich organic soils
        in grassland areas. The drainage of organic soils can significantly
        increase CH4 emissions due to the exposure of previously waterlogged organic matter
        to conditions that promote methane production.

        Emission factors are sourced from a country-specific database, ensuring that the
        emissions estimation is relevant to the regional characteristics of grassland drainage.

        Returns:
            float: The calculated CH4 emissions in kg from organic soils in grassland areas.
            The emissions are based on the current area of drained land and a combination
            of the emission factors for land drainage and ditch drainage.
        """
        ef_ch4_grassland_drainage_land_poor = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_ch4_grassland_drainage_land_poor"
            )
        )

        ef_ch4_grassland_drainage_land_rich = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_ch4_grassland_drainage_land_rich"
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

        emission_poor = self.current_area_drained_poor * (
            (1.0 - frac_ditch) * ef_ch4_grassland_drainage_land_poor
            + frac_ditch * ef_ch4_grassland_drainage_ditch
        )

        emission_rich = self.current_area_drained_rich * (
            (1.0 - frac_ditch) * ef_ch4_grassland_drainage_land_rich
            + frac_ditch * ef_ch4_grassland_drainage_ditch
        )

        return emission_poor + emission_rich
    

    def drainage_n2O_organic_soils_in_grassland(self):
        """
        Calculates the nitrous oxide (N2O) emissions resulting from the drainage of poor and rich organic
        soils in grassland areas. Drainage of organic soils in grasslands can lead to increased N2O emissions.
        This is due to the changes in soil conditions that promote nitrification and denitrification processes,
        which are major sources of N2O emissions.

        This method estimates N2O emissions by applying an emission factor specific to
        grassland drainage.

        Returns:
            float: The calculated N2O emissions in kg resulting from the drainage of organic soils in grassland areas.
            The emissions are based on the current area of drained land and the specific emission factors for
            N2O emissions from grassland drainage.
        """
        ef_n2o_grassland_drainage_poor = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_n2o_grassland_drainage_poor"
            )
        )

        ef_n2o_grassland_drainage_rich = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_n2o_grassland_drainage_rich"
            )
        )

        emission_poor = self.current_area_drained_poor * ef_n2o_grassland_drainage_poor
        emission_rich = self.current_area_drained_rich * ef_n2o_grassland_drainage_rich

        return emission_poor + emission_rich

    def rewetting_co2_organic_soils_in_grassland(self):
        """
        Calculates the carbon dioxide (CO2) emissions/removals resulting from the rewetting
        of drained rich and poor organic soils in grassland areas. 

        This method considers two key emission reduction factors: direct
        on-site CO2 emissions/removals due to rewetting and the CO2 emissions related
        to dissolved organic carbon (DOC). 

        Returns:
            float: The calculated CO2 emissions/removals in kg reductions resulting from the rewetting of
            organic soils in grassland areas. 

        """

        onsite_emissions = self.rewetting_co2_onsite_organic_soils_in_grassland()
        offsite_emissions = self.rewetting_co2_offsite_organic_soils_in_grassland()

        return onsite_emissions + offsite_emissions
    
    
    def rewetting_co2_onsite_organic_soils_in_grassland(self):
        """
        Calculates the carbon dioxide (CO2) emissions resulting from the rewetting of poor and rich organic soils
        in grassland areas.

        This method focuses specifically on CO2 emissions from on-site sources in grasslands
        where organic soils have been rewetted.

        Returns:
            float: The calculated CO2 emissions in kg resulting from the rewetting of poor and rich organic soils
            in grassland areas. The emissions are based on the current area of rewetted land and the specific emission factors 
            for CO2 emissions from grassland rewetting.
        """
        ef_co2_grassland_rewetting_on_site_poor = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_grassland_rewetting_on_site_poor"
            )
        )

        ef_co2_grassland_rewetting_on_site_rich = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_grassland_rewetting_on_site_rich"
            )
        )

        emissions_poor = self.current_area_rewetted_poor * ef_co2_grassland_rewetting_on_site_poor
        emissions_rich = self.current_area_rewetted_rich * ef_co2_grassland_rewetting_on_site_rich

        return emissions_poor + emissions_rich
    

    def rewetting_co2_offsite_organic_soils_in_grassland(self):
        """
        Calculates the offsite CO2 emissions, in the form of Disolved Organic Carbon (DOC) from the rewetting of poor and rich organic
        soils in grassland areas.

        A tier 1 approach is used to estimate the DOC emissions from the rewetted organic soils in grasslands.

        Returns:
            float: The calculated CO2 emissions in kg resulting from the rewetting of poor and rich organic soils
                in grassland areas. The emissions are based on the current area of rewetted
                land and the specific emission factor for CO2 emissions from grassland rewetting.
        """
        ef_co2_grassland_rewetting_DOC = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_grassland_rewetting_DOC"
            )
        )

        return (self.current_area_rewetted_poor + self.current_area_rewetted_rich) * ef_co2_grassland_rewetting_DOC


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
        """
        ef_ch4_grassland_rewetting_poor = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_ch4_grassland_rewetting_poor"
            )
        )

        ef_ch4_grassland_rewetting_rich = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_ch4_grassland_rewetting_rich"
            )
        )

        emissions_poor = self.current_area_rewetted_poor * ef_ch4_grassland_rewetting_poor
        emissions_rich = self.current_area_rewetted_rich * ef_ch4_grassland_rewetting_rich

        return emissions_poor + emissions_rich
    

    def burning_co2_grassland(self, include_peat_fire_co2=False):
        """
        CO2 from grassland fires on organic (peat) soil, in tonnes. Returns 0 unless include_peat_fire_co2 is True.

        **Not counted under the national inventory.** NID 2026 s.6.5.4 (Tier 1) estimates grassland fire CH4 and
        N2O only; CRT 2026 4(IV).C.1 reports CO2 as NO. So the default (False) gives 0, and grassland fire CO2 is
        not in total_co2_emission_grassland.

        The IPCC 2013 Wetlands Supplement (s.2.2.2.3, eq 2.8) asks for CO2 from fires on managed organic soils,
        because burnt peat does not grow back. include_peat_fire_co2=True gives that calculation,
        L = A x MB.Cf x Gef x 1e-3, with the burnt share applied equally to each organic soil type:
            drained organic soil  MB.Cf 336 t DM/ha, Gef 362 g CO2-C/kg DM (x 44/12 on read)
            undrained organic     MB.Cf 66 t DM/ha,  Gef 362 g CO2-C/kg DM (package "rewetted" grassland)
        MB.Cf from NID 2026 Table 6.34; Gef from IPCC 2013 WS Table 2.7 (NID Table 6.34 prints it as g CO2).
        Mineral soil is never charged CO2: burnt grass regrows, and neither the IPCC Tier 1 nor the NID counts it.

        Parameters:
            include_peat_fire_co2 (bool): False (default) returns 0, as in the inventory. True returns the
                organic-soil (peat) fire CO2.

        Returns:
            float: CO2 emissions from grassland peat fires (t).
        """
        if not include_peat_fire_co2:
            return 0.0

        get = self.emissions_factors.get_emission_factor_in_emission_factor_data_base

        fire_undrained_organic_soil = (
            (self.current_area_rewetted_poor + self.current_area_rewetted_rich)
            * self.land_use_data.grassland.share_burnt
            * get("ef_wildfire_MB_time_CF_wet_organic_soil_grassland")
            * get("ef_wildfire_GEF_co2_wet_organic_soil_grassland")
            * 10**-3
        )
        fire_drained_organic_soil = (
            (self.current_area_drained_poor + self.current_area_drained_rich)
            * self.land_use_data.grassland.share_burnt
            * get("ef_wildfire_MB_time_CF_drained_organic_soil_grassland")
            * get("ef_wildfire_GEF_co2_drained_organic_soil_grassland")
            * 10**-3
        )

        return fire_undrained_organic_soil + fire_drained_organic_soil


    def burning_ch4_grassland(self):
        """
        CH4 from grassland fires, in tonnes (NID 2026 s.6.5.4, IPCC eq 2.27: L = A x MB.Cf x Gef x 1e-3).

        Factors are NID 2026 Table 6.34: MB.Cf 4.1 / 336 / 66 t/ha and Gef CH4 2.3 / 9 / 9 g/kg dry matter
        for mineral / drained organic / undrained organic soil (package "rewetted" grassland).

        **Soil split differs from the NID.** The package applies share_burnt equally to each soil type, so the
        burnt area follows the soil areas (about 8% organic in the inventory). The NID puts much more of the
        burnt area on organic soil (it counts half of peatland fires as rough grazing; about 87% of the dry
        matter burnt is organic, from the CRT CH4/N2O ratio) and does not publish its split. With the
        inventory's own areas the package gives 0.57-0.72x the CRT CH4 (2020-2022). Kept on purpose: it needs
        no unpublished split and keeps the response to drainage and rewetting.

        Returns:
            float: CH4 emissions from grassland fires (t).
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
                self.current_area_mineral * self.land_use_data.grassland.share_burnt
            )
            * ef_wildfire_MB_time_CF_mineral_soil_grassland
            * ef_wildfire_GEF_ch4_mineral
            * 10**-3
        )
        fire_undrained_organic_soil = (
            (
                (self.current_area_rewetted_poor + self.current_area_rewetted_rich)
                * self.land_use_data.grassland.share_burnt
            )
            * ef_wildfire_MB_time_CF_wet_organic_soil_grassland
            * ef_wildfire_GEF_ch4_wet
            * 10**-3
        )
        fire_drained_organic_soil = (
            (
                (self.current_area_drained_poor + self.current_area_drained_rich)
                * self.land_use_data.grassland.share_burnt
            )
            * ef_wildfire_MB_time_CF_drained_organic_soil_grassland
            * ef_wildfire_GEF_ch4_drained
            * 10**-3
        )

        return fire_mineral_soil + fire_drained_organic_soil + fire_undrained_organic_soil

    def burning_n2o_grassland(self):
        """
        N2O from grassland fires, in tonnes (NID 2026 s.6.5.4, IPCC eq 2.27: L = A x MB.Cf x Gef x 1e-3).

        Factors are NID 2026 Table 6.34: MB.Cf 4.1 / 336 / 66 t/ha and Gef N2O 0.21 / 0.21 / 0.21 g/kg dry matter
        for mineral / drained organic / undrained organic soil (package "rewetted" grassland).

        **Soil split differs from the NID.** The package applies share_burnt equally to each soil type, so the
        burnt area follows the soil areas (about 8% organic in the inventory). The NID puts much more of the
        burnt area on organic soil (it counts half of peatland fires as rough grazing; about 87% of the dry
        matter burnt is organic, from the CRT CH4/N2O ratio) and does not publish its split. With the
        inventory's own areas the package gives 0.57-0.72x the CRT N2O (2020-2022). Kept on purpose: it needs
        no unpublished split and keeps the response to drainage and rewetting.

        Returns:
            float: N2O emissions from grassland fires (t).
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
                self.current_area_mineral * self.land_use_data.grassland.share_burnt
            )
            * ef_wildfire_MB_time_CF_mineral_soil_grassland
            * ef_wildfire_GEF_n2o_grassland_mineral
            * 10**-3
        )
        fire_undrained_organic_soil = (
        (
            (self.current_area_rewetted_poor + self.current_area_rewetted_rich)
            * self.land_use_data.grassland.share_burnt
        )
        * ef_wildfire_MB_time_CF_wet_organic_soil_grassland
        * ef_wildfire_GEF_n2o_grassland_wet
        * 10**-3
        )

        fire_drained_organic_soil = (
            (
                (self.current_area_drained_poor + self.current_area_drained_rich)
                * self.land_use_data.grassland.share_burnt
            )
            * ef_wildfire_MB_time_CF_drained_organic_soil_grassland
            * ef_wildfire_GEF_n2o_grassland_drained
            * 10**-3
        )

        return fire_mineral_soil + fire_drained_organic_soil + fire_undrained_organic_soil

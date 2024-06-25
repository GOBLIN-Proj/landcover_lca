from landcover_lca.geo_goblin.land_classes.landuse import LandUse

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
            * self.land_use_data.grassland.share_organic
        )

        self.current_area_drained_poor = (
            self.land_use_data.grassland.area_ha
            * self.land_use_data.grassland.share_organic_mineral
        )


        self.current_area_rewetted_poor = (
            self.land_use_data.grassland.area_ha
            * self.land_use_data.grassland.share_rewetted_in_organic
        )

        self.current_area_rewetted_rich = (
            self.land_use_data.grassland.area_ha
            * self.land_use_data.grassland.share_rewetted_in_organic_mineral
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
            (self.current_area_mineral
            * self.land_use_data.grassland.share_burnt)
            * ef_wildfire_MB_time_CF_mineral_soil_grassland
            * ef_wildfire_GEF_co2_mineral
            * 10**-3
        )
        fire_undrained_organic_soil = (
            (
            (self.current_area_rewetted_poor + self.current_area_rewetted_rich)
            * self.land_use_data.grassland.share_burnt
            )
            * ef_wildfire_MB_time_CF_wet_organic_soil_grassland
            * ef_wildfire_GEF_co2_wet
            * 10**-3
        )
        fire_drained_organic_soil = (
            (
                (self.current_area_drained_poor + self.current_area_drained_rich)
                * self.land_use_data.grassland.share_burnt
            )
            * ef_wildfire_MB_time_CF_drained_organic_soil_grassland
            * ef_wildfire_GEF_co2_drained
            * 10**-3
        )

        return (fire_mineral_soil + fire_undrained_organic_soil + fire_drained_organic_soil)


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

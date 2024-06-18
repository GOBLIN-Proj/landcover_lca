from landcover_lca.land_classes.landuse import LandUse

class Wetland(LandUse):
    """
    A class representing a wetland land use.

    Attributes:
        - current_area_mineral (float): The current area of mineral wetland in hectares.
        - current_area_unmanaged (float): The current area of unmanaged wetland in hectares.
        - current_area_near_natural (float): The current area of near-natural wetland in hectares.
        - current_area_domestic_drained (float): The current area of wetland drained for domestic peat extraction in hectares.
        - current_area_industrial_drained (float): The current area of wetland drained for industrial peat extraction in hectares.
        - current_area_domestic_rewetted (float): The current area of wetland rewetted after domestic peat extraction in hectares.
        - current_area_industrial_rewetted (float): The current area of wetland rewetted after industrial peat extraction in hectares.


    Methods:
        - co2_removals(): Calculate the amount of CO2 removals per year for a given area.
        - co2_emissions_wetland_drained(): Calculate the CO2 emissions from wetland drainage.
        - drainage_ch4_organic_soils(): Calculate the methane emissions from organic soils due to drainage.
        - drainage_n2o_organic_soils(): Calculate the nitrous oxide emissions from organic soils due to drainage.
        - rewetting_co2_organic_soils(): Calculate the CO2 emissions from rewetting organic soils.
        - rewetting_ch4_organic_soils_in_wetland(): Calculate the methane emissions from rewetting organic soils.
        - burning_co2_wetland(): Calculate the CO2 emissions from burning wetland vegetation.
        - burning_ch4_wetland(): Calculate the CH4 emissions from burning wetland vegetation.
        - burning_n2o_wetland(): Calculate the N2O emissions from burning wetland vegetation.

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

        self.current_area_mineral= (
            self.land_use_data.wetland.area_ha
            * self.land_use_data.wetland.share_mineral
        )

        self.current_area_unmanaged = (
            self.land_use_data.wetland.area_ha
            * self.land_use_data.wetland.share_unmanaged_wetland
        )

        self._current_area_near_natural = (
            self.land_use_data.wetland.area_ha
            * self.land_use_data.wetland.share_near_natural_wetland
        )

        self.current_area_domestic_drained = (
            self.land_use_data.wetland.area_ha
            * self.land_use_data.wetland.share_domestic_peat_extraction
        )

        self.current_area_industrial_drained = (
            self.land_use_data.wetland.area_ha
            * self.land_use_data.wetland.share_industrial_peat_extraction
        )

        self.current_area_domestic_rewetted = (
            self.land_use_data.wetland.area_ha
            * self.land_use_data.wetland.share_rewetted_domestic_peat_extraction
        )

        self.current_area_industrial_rewetted = (
            self.land_use_data.wetland.area_ha
            * self.land_use_data.wetland.share_rewetted_industrial_peat_extraction
        )

        
    def co2_removals(self):
        """
        Calculate the amount of CO2 removals per year for a given area.
        return 0.6t C per year for 5 years for area drained.

        Returns:
            float: The total amount of CO2 removals in kg over the specified year range.
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
        Calculates the carbon dioxide (CO2) emissions resulting from the drainage of wetland areas.
        Draining wetlands can lead to significant CO2 emissions due to the exposure of previously
        waterlogged organic matter to aerobic conditions, accelerating its decomposition and
        subsequent release of stored carbon.

        This method considers the CO2 emissions from different sources, including industrial and
        domestic drainage, as well as emissions from unmanaged and near-natural wetlands.

        The emission factors for each source are retrieved from a database of country-specific

        Returns:
            float: The total CO2 emissions in kg from wetland drainage, including emissions from
                industrial and domestic drainage, as well as unmanaged and near-natural wetlands.
        """
        industral_drained = self.co2_emissions_industrial_drained_onsite() + self.co2_emissions_industrial_drained_offsite()
        domestic_drained = self.co2_emissions_domestic_drained_onsite() + self.co2_emissions_domestic_drained_offsite()
        unmanaged_and_near_natural = self.co2_emissions_unmanaged_and_near_natural_onsite() + self.co2_emissions_unmanaged_and_near_natural_offsite()

        return industral_drained + domestic_drained + unmanaged_and_near_natural


    def co2_emissions_industrial_drained_onsite(self):
        """
        Calculates the carbon dioxide (CO2) emissions resulting from the drainage of industrial
        wetlands onsite.

        Returns:
            float: The calculated CO2 emissions in kg from industrial wetland drainage onsite.
        """
        ef_co2_industrail_drained_onsite = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_wetland_industrial_extraction_on_site"
            )
        )

        return self.current_area_industrial_drained * ef_co2_industrail_drained_onsite
    
    def co2_emissions_industrial_drained_offsite(self):
        """
        Calculates the carbon dioxide (CO2) emissions resulting from the drainage of industrial
        wetlands offsite.

        Returns:
            float: The calculated CO2 emissions in kg from industrial wetland drainage offsite.
        """
        ef_co2_industrail_drained_offsite = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_wetland_drainage_DOC_default"
            )
        )

        return self.current_area_industrial_drained * ef_co2_industrail_drained_offsite


    def co2_emissions_domestic_drained_onsite(self):
        """
        Calculates the carbon dioxide (CO2) emissions resulting from the drainage of domestic
        wetlands onsite.

        Returns:
            float: The calculated CO2 emissions in kg from domestic wetland drainage onsite.
        """
        ef_co2_domestic_drained_onsite = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_wetland_domestic_extraction_on_site"
            )
        )

        return self.current_area_domestic_drained * ef_co2_domestic_drained_onsite
    

    def co2_emissions_domestic_drained_offsite(self):
        """
        Calculates the carbon dioxide (CO2) emissions resulting from the drainage of domestic
        wetlands offsite.

        Returns:
            float: The calculated CO2 emissions in kg from domestic wetland drainage offsite.
        """
        ef_co2_domestic_drained_offsite = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_wetland_drainage_DOC_default"
            )
        )

        return self.current_area_domestic_drained * ef_co2_domestic_drained_offsite


    def co2_emissions_unmanaged_and_near_natural_onsite(self):
        """
        Calculates the carbon dioxide (CO2) emissions resulting from the drainage of unmanaged
        and near-natural wetlands onsite.

        Returns:
            float: The calculated CO2 emissions in kg from unmanaged and near-natural wetland drainage onsite.
        """
        ef_co2_unmanaged_and_near_natural_onsite = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_near_natural_wetland_removal"
            )
        )

        return self.current_area_unmanaged * ef_co2_unmanaged_and_near_natural_onsite


    def co2_emissions_unmanaged_and_near_natural_offsite(self):
        """
        Calculates the carbon dioxide (CO2) emissions resulting from the drainage of unmanaged
        and near-natural wetlands offsite.

        Returns:
            float: The calculated CO2 emissions in kg from unmanaged and near-natural wetland drainage offsite.
        """
        ef_co2_unmanaged_and_near_natural_offsite = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_near_natural_wetland_runoff"
            )
        )

        return self.current_area_unmanaged * ef_co2_unmanaged_and_near_natural_offsite


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
            float: The calculated CH4 emissions in kg from organic soils due to drainage.
                This is based on the current area of drained land, the proportion of land drained by ditches,
                and the respective emission factors for each type of drainage.

        """
        ef_ch4_drainage_peatland_land = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_ch4_wetland_drainage_land_default"
            )
        )
        ef_ch4_drainage_peatland_ditch = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_ch4_wetland_drainage_ditch_default"
            )
        )

        frac_ditch = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "frac_ditch"
            )
        )

        area_drained = self.current_area_domestic_drained + self.current_area_industrial_drained

        return area_drained * (
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

        Returns:
            float: The calculated N2O emissions in kg resulting from the drainage of organic soils.
        """
        ef_n2o_drainage_wetland_to_peatland = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_n2o_wetland_drainage_default"
            )
        )

        drained_area = self.current_area_domestic_drained + self.current_area_industrial_drained

        return drained_area * ef_n2o_drainage_wetland_to_peatland


    def rewetting_co2_organic_soils(self):
        """
        Calculates the carbon dioxide (CO2) emissions resulting from the rewetting of organic
        soils, such as peatlands. Rewetting of drained peatlands can lead to the release of
        stored carbon, as the waterlogged conditions promote anaerobic decomposition of
        organic matter, releasing CO2 into the atmosphere.

        Returns:
            float: The calculated CO2 emissions in kg from the rewetting of organic soils.
    
        """
    
        onsite = self.co2_emissions_default_rewetted_onsite()
        offsite = self.co2_emissions_default_rewetted_offsite()

        return onsite + offsite

    def co2_emissions_default_rewetted_onsite(self):
        """
        Calculates the carbon dioxide (CO2) emissions resulting from the rewetting of wetlands
        onsite using tier 1 default emission factors.

        Returns:
            float: The calculated CO2 emissions in kg from wetland rewetting onsite.
        """
        ef_co2_rewetted_onsite = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_wetland_rewet_on_site_default"
            )
        )

        return (self.current_area_domestic_rewetted + self.current_area_industrial_rewetted) * ef_co2_rewetted_onsite


    def co2_emissions_default_rewetted_offsite(self):
        """
        Calculates the carbon dioxide (CO2) emissions resulting from the rewetting of wetlands
        offsite using tier 1 default emission factors.

        Returns:
            float: The calculated CO2 emissions in kg from wetland rewetting offsite.
        """
        ef_co2_rewetted_offsite = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_wetland_rewet_off_site_deafult"
            )
        )

        return (self.current_area_domestic_rewetted + self.current_area_industrial_rewetted) * ef_co2_rewetted_offsite


    def rewetting_ch4_organic_soils_in_wetland(self):
        """
        Calculates the methane (CH4) emissions resulting from the rewetting of organic soils,
        such as peatlands. Rewetting of drained peatlands can lead to the release of methane,
        a potent greenhouse gas, due to the anaerobic decomposition of organic matter under
        waterlogged conditions.


        Returns:
            float: The calculated CH4 emissions in kg from the rewetting of organic soils.
        """

        ef_ch4_peatland_to_wetland_rewetting = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_ch4_wetland_rewet_off_site_deafult"
            )
        )

        area_rewetted = self.current_area_domestic_rewetted + self.current_area_industrial_rewetted

        return area_rewetted * ef_ch4_peatland_to_wetland_rewetting

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
        """
        ef_wetland_fuel_burning = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_wildfire_MB_time_CF_wetland"
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
        """
        ef_wetland_fuel_burning = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_wildfire_MB_time_CF_wetland"
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
        """
        ef_wetland_fuel_burning = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_wildfire_MB_time_CF_wetland"
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
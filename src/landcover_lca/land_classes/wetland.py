from landcover_lca.land_classes.landuse import LandUse

class Wetland(LandUse):
    """
    A class representing a wetland land use.

    Attributes:
        - current_area_mineral (float): The current area of mineral wetland in hectares.
        - current_area_unmanaged (float): The current area of unmanaged wetland in hectares. Area only: no
          emissions are calculated for it (NID 2026 s.6.6.1: "only the area of these lands is reported").
        - current_area_near_natural (float): The current area of near-natural wetland in hectares.
        - current_area_domestic_drained (float): The current area of wetland drained for domestic peat extraction in hectares.
        - current_area_industrial_drained (float): The current area of wetland drained for industrial peat extraction in hectares.
        - current_area_domestic_rewetted (float): The current area of wetland rewetted after domestic peat extraction in hectares.
        - current_area_industrial_rewetted (float): The current area of wetland rewetted after industrial peat extraction in hectares.


    Methods:
        - co2_removals(): Calculate the amount of CO2 removals per year for a given area.
        - co2_emissions_wetland_drained(): Calculate the CO2 emissions from wetland drainage.
        - co2_emissions_industrial_drained_onsite(): Calculate the CO2 emissions from industrial wetland drainage onsite.
        - co2_emissions_industrial_drained_offsite(): Calculate the CO2 emissions from industrial wetland drainage offsite.
        - co2_emissions_domestic_drained_onsite(): Calculate the CO2 emissions from domestic wetland drainage onsite.
        - co2_emissions_domestic_drained_offsite(): Calculate the CO2 emissions from domestic wetland drainage offsite.
        - co2_emissions_unmanaged_and_near_natural_onsite(): On-site CO2 of near-natural wetland (a removal).
        - co2_emissions_unmanaged_and_near_natural_offsite(): Off-site (runoff) CO2 of near-natural wetland.
        - ch4_emissions_unmanaged_and_near_natural(): CH4 of near-natural wetland.
          These three use the near-natural area only; the names are kept for compatibility.
        - drainage_ch4_organic_soils(): Calculate the CH4 emissions from organic soils due to drainage.
        - drainage_n2o_organic_soils(): Calculate the N2O emissions from organic soils due to drainage.
        - rewetting_co2_organic_soils(): Calculate the CO2 emissions from rewetting organic soils.
        - co2_emissions_default_rewetted_onsite(): Calculate the CO2 emissions from rewetting wetlands onsite.
        - co2_emissions_default_rewetted_offsite(): Calculate the CO2 emissions from rewetting wetlands offsite.
        - rewetting_ch4_organic_soils_in_wetland(): Calculate the CH4 emissions from rewetting organic soils in wetlands.
        - burning_co2_wetland(): Calculate the CO2 emissions from burning wetlands.
        - burning_ch4_wetland(): Calculate the CH4 emissions from burning wetlands.
        - burning_n2o_wetland(): Calculate the N2O emissions from burning wetlands.
        

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
        CO2 removal by vegetation re-establishing on restored (rewetted) peatland, in kg CO2 in the target year.

        NID 2026 s.6.6.4.1 (p.279-280): vegetation returns on restored cutaway over 5 years, to 3 t C/ha
        (Cruickshank et al. 2000), i.e. 0.6 t C/ha/yr; the restoration area is the annual increase in cutaway.
        ``ef_co2_peatland_to_wetland_biomass`` = -3.0 t C/ha in total, read as kg CO2/ha.
        Same convention as the soil carbon change (D1): the area of ``Wetland_to_Wetland`` is spread evenly over
        the span (``annual_area``), and in the target year the land restored in the last 5 years is still
        accumulating:

            removal = annual_area x min(span, 5) x factor / 5

        A span of 0 gives 0 (no area moved). The inventory does not report this gain separately (CRT 4.D.1
        biomass gains are "IE"), and the default GOBLIN inputs have ``Wetland_to_Wetland`` = 0, so it is 0 there.

        Returns:
            float: CO2 in kg (negative = removal).

        Raises:
            ValueError: if the span is negative.
        """
        if self.year_range < 0:
            raise ValueError(f"time span must not be negative, got {self.year_range}")

        if not self.annual_area:
            return 0.0

        biomass_removal_factor = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_peatland_to_wetland_biomass"
            )
        )

        return self.annual_area * min(self.year_range, 5) * biomass_removal_factor / 5

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
        industrial_drained = self.co2_emissions_industrial_drained_onsite() + self.co2_emissions_industrial_drained_offsite()
        domestic_drained = self.co2_emissions_domestic_drained_onsite() + self.co2_emissions_domestic_drained_offsite()
        unmanaged_and_near_natural = self.co2_emissions_unmanaged_and_near_natural_onsite() + self.co2_emissions_unmanaged_and_near_natural_offsite()

        return industrial_drained + domestic_drained + unmanaged_and_near_natural


    def co2_emissions_industrial_drained_onsite(self):
        """
        Calculates the carbon dioxide (CO2) emissions resulting from the drainage of industrial
        wetlands onsite.

        Returns:
            float: The calculated CO2 emissions in kg from industrial wetland drainage onsite.
        """
        ef_co2_industrial_drained_onsite = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_wetland_industrial_extraction_on_site"
            )
        )

        return self.current_area_industrial_drained * ef_co2_industrial_drained_onsite
    
    def co2_emissions_industrial_drained_offsite(self):
        """
        Calculates the carbon dioxide (CO2) emissions resulting from the drainage of industrial
        wetlands offsite.

        Returns:
            float: The calculated CO2 emissions in kg from industrial wetland drainage offsite.
        """
        ef_co2_industrial_drained_offsite = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_wetland_drainage_DOC_default"
            )
        )

        return self.current_area_industrial_drained * ef_co2_industrial_drained_offsite


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
        On-site CO2 of near-natural (undrained) wetland: -0.33 t CO2-C/ha/yr, a removal (NID 2026 s.6.6.4.2,
        Aitova et al. 2023). Near-natural area only; unmanaged wetland is area only (NID s.6.6.1).

        Returns:
            float: CO2 in kg (negative = removal).
        """
        ef_co2_unmanaged_and_near_natural_onsite = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_near_natural_wetland_removal"
            )
        )

        return self._current_area_near_natural * ef_co2_unmanaged_and_near_natural_onsite


    def co2_emissions_unmanaged_and_near_natural_offsite(self):
        """
        Off-site CO2 of near-natural wetland: dissolved organic carbon in runoff, 0.17 t CO2-C/ha/yr
        (NID 2026 s.6.6.4.2). Near-natural area only.

        Returns:
            float: CO2 in kg.
        """
        ef_co2_unmanaged_and_near_natural_offsite = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_near_natural_wetland_runoff"
            )
        )

        return self._current_area_near_natural * ef_co2_unmanaged_and_near_natural_offsite

    def ch4_emissions_unmanaged_and_near_natural(self):
        """
        CH4 of near-natural (undrained) wetland: 54.7 kg CH4-C/ha/yr (NID 2026 s.6.6.4.2, Aitova et al. 2023).
        Near-natural area only.

        Returns:
            float: CH4 in kg.
        """
        ef_ch4_unmanaged_and_near_natural = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_ch4_near_natural_wetland"
            )
        )

        return  self._current_area_near_natural * ef_ch4_unmanaged_and_near_natural
    

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
                "ef_co2_wetland_rewet_off_site_default"
            )
        )

        return (self.current_area_domestic_rewetted + self.current_area_industrial_rewetted) * ef_co2_rewetted_offsite


    def rewetting_ch4_organic_soils_in_wetland(self):
        """
        CH4 from rewetted peat-extraction land, in kg: each area times its own factor.

        - Rewetted industrial: ``ef_ch4_wetland_rewet_industrial``, 216 kg CH4/ha (NID 2026 s.6.6.4.2, the
          nutrient-rich value, applied as kg CH4 as the NID does; IPCC 2013 Wetlands Supplement Table 3.3).
        - Rewetted domestic: ``ef_ch4_wetland_rewet_domestic``, 106.4 kg CH4/ha, the CRT 2026 4(II) "Other
          Domestic Peat Extraction" implied factor. The NID does not state it: it is a weighted average of the
          NID's 216 (rich) and 92 (poor) kg CH4/ha, about 12% rich.

        One factor per category, because the inventory publishes no rich/poor split of the rewetted areas.

        Returns:
            float: CH4 in kg.
        """
        get = self.emissions_factors.get_emission_factor_in_emission_factor_data_base

        return (
            self.current_area_domestic_rewetted * get("ef_ch4_wetland_rewet_domestic")
            + self.current_area_industrial_rewetted * get("ef_ch4_wetland_rewet_industrial")
        )


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
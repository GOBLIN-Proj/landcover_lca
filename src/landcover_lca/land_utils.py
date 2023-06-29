import numpy as np
from landcover_lca.data_loader import Loader
from landcover_lca.models import Emissions_Factors, Land_Use_Features


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

        years = tuple(
            (
                self.land_use_data.__getattribute__(self.current_land_use).year,
                self.past_land_use_data.__getattribute__(self.current_land_use).year,
            )
        )

        scenario_period = years[0] - years[1]

        return scenario_period

    def compute_SOC_ref_for_land_use(self):
        return np.sum(
            self.ipcc_soil_class_SOC["Proportion"] * self.ipcc_soil_class_SOC["SOCref"]
        )

    def compute_land_use_change_total_area(self):
        """
        Get the annual area converted.
        """

        land_use_total_area = self.transition_matrix_data.__dict__[
            f"{self.past_land_use}_to_{self.current_land_use}"
        ]

        try:
            land_use_annual_area = land_use_total_area / self.year_range

            return land_use_annual_area

        except ZeroDivisionError:

            return 0

    def compute_emission_factor_from_mineral_soils(self, land_use_name):

        FLU = (
            self.land_use_features.get_landuse_features_in_land_use_features_data_base(
                "FLU", land_use_name
            )
        )
        FMG = (
            self.land_use_features.get_landuse_features_in_land_use_features_data_base(
                "FMG", land_use_name
            )
        )
        FI = self.land_use_features.get_landuse_features_in_land_use_features_data_base(
            "FI", land_use_name
        )
        Adjustement_factor = (
            self.land_use_features.get_landuse_features_in_land_use_features_data_base(
                "Adjustement_factor", land_use_name
            )
        )

        SOC_ref = self.compute_SOC_ref_for_land_use()

        return SOC_ref * Adjustement_factor

    def compute_emissions_from_mineral_soils_in_land_use_change(self):
        """
        Total soc change is calculated and then spread evenly over a 20 year transition period
        """

        EF_SOC_previous_land_use = self.compute_emission_factor_from_mineral_soils(
            self.past_land_use
        )

        EF_SOC_current_land_use = self.compute_emission_factor_from_mineral_soils(
            self.current_land_use
        )

        annual_area = self.compute_land_use_change_total_area()

        transition_period = 20

        soc = 0
        if annual_area:
            for year in range(self.year_range):
                if year < 20:
                    soc += (
                        annual_area
                        * (EF_SOC_current_land_use - EF_SOC_previous_land_use)
                    ) / transition_period
                else:
                    return soc
        else:
            return soc


class LandUse:
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
        Get the annual area converted.
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

        return self.transition_matrix_data.__dict__[
            f"{self.past_land_use}_to_{self.current_land_use}"
        ]

    def compute_total_land_use_area(self):

        land_use_total_area = self.land_use_data.__getattribute__(
            self.current_land_use
        ).area_ha

        return land_use_total_area


class Wetland(LandUse):
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

        self.current_area_drained = (
            self.land_use_data.wetland.area_ha
            * self.land_use_data.wetland.share_peat_extraction
        )

    def co2_removals(self):
        """
        return 0.6t C per year for 5 years for area drained.
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

        ef_co2_wetland_drainage_on_site = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_wetland_drainage_on_site"
            )
        )
        ef_co2_wetland_drainage_DOC = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_wetland_drainage_DOC"
            )
        )

        current_area_drained = (
            self.past_land_use_data.wetland.area_ha
            * self.past_land_use_data.wetland.share_peat_extraction
        )

        return current_area_drained * (
            ef_co2_wetland_drainage_on_site + ef_co2_wetland_drainage_DOC
        )

    def drainage_ch4_organic_soils(self):
        ef_ch4_drainage_peatland_land = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_ch4_wetland_drainage_land"
            )
        )
        ef_ch4_drainage_peatland_ditch = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_ch4_wetland_drainage_ditch"
            )
        )

        frac_ditch = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "frac_ditch"
            )
        )

        return self.current_area_drained * (
            (1.0 - frac_ditch) * ef_ch4_drainage_peatland_land
            + frac_ditch * ef_ch4_drainage_peatland_ditch
        )

    def drainage_n2o_organic_soils(self):

        ef_n2o_drainage_wetland_to_peatland = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_n2o_wetland_drainage"
            )
        )

        return self.current_area_drained * ef_n2o_drainage_wetland_to_peatland

    def rewetting_co2_organic_soils(self):

        """
        REturn nothing for the time being as we are estimating the rewetting of grassland and not wetlands
        """
        ef_co2_peatland_to_wetland_rewetting_on_site = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_wetland_rewetting_on_site"
            )
        )
        ef_co2_peatland_to_wetland_rewetting_DOC = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_wetland_rewetting_DOC"
            )
        )

    def rewetting_ch4_organic_soils_in_wetland(self):

        """
        REturn nothing for the time being as we are estimating the rewetting of grassland and not wetlands
        """

        ef_ch4_peatland_to_wetland_rewetting = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_ch4_wetland_rewetting"
            )
        )

    def burning_co2_wetland(self):
        ef_wetland_fuel_burning = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_wetland_fuel_burning"
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
        ef_wetland_fuel_burning = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_wetland_fuel_burning"
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
        ef_wetland_fuel_burning = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_wetland_fuel_burning"
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


class Grassland(LandUse):
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

        self.current_area_drained = (
            self.land_use_data.grassland.area_ha
            * self.land_use_data.grassland.share_organic
        )

    def drainage_co2_organic_soils_in_grassland(self):
        ef_co2_grassland_drainage_on_site = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_grassland_drainage_on_site"
            )
        )

        return self.current_area_drained * ef_co2_grassland_drainage_on_site

    def drainage_ch4_organic_soils_in_grassland(self):
        ef_ch4_grassland_drainage_land = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_ch4_grassland_drainage_land"
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

        return self.current_area_drained * (
            (1.0 - frac_ditch) * ef_ch4_grassland_drainage_land
            + frac_ditch * ef_ch4_grassland_drainage_ditch
        )

    def drainage_n2O_organic_soils_in_grassland(self):
        ef_n2o_grassland_drainage = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_n2o_grassland_drainage"
            )
        )

        return self.current_area_drained * ef_n2o_grassland_drainage

    def rewetting_co2_organic_soils_in_grassland(self):
        ef_co2_grassland_rewetting_on_site = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_grassland_rewetting_on_site"
            )
        )
        ef_co2_grassland_rewetting_DOC = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_grassland_rewetting_DOC"
            )
        )

        return (
            ef_co2_grassland_rewetting_on_site + ef_co2_grassland_rewetting_DOC
        ) * self.total_transition_area

    def rewetting_ch4_organic_soils_in_grassland(self):

        ef_ch4_grassland_rewetting = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_ch4_grassland_rewetting"
            )
        )

        return ef_ch4_grassland_rewetting * self.total_transition_area

    def burning_co2_grassland(self):
        """
        𝐿𝑓𝑖𝑟𝑒 = 𝐴 ∙ 𝑀𝐵 ∙ 𝐶𝑓 ∙ 𝐺𝑒𝑓 ∙ 10^−3

        For Cf (Combustion factor), it is assumed that all the available fuel is burned,
        thus the value used is 1.0.

        """

        ef_wildfire_MB_time_CF_mineral_soil_grassland = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_wildfire_GEF_ch4_mineral_soil_grassland"
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
            (
                self.land_use_data.grassland.area_ha
                * self.land_use_data.grassland.share_burnt
                * self.land_use_data.grassland.share_mineral
            )
            * ef_wildfire_MB_time_CF_mineral_soil_grassland
            * ef_wildfire_GEF_co2_mineral
            * 10**-3
        )
        # fire_undrained_organic_soil = (
        # (
        # self.land_use_data.grassland.area_ha
        # * self.land_use_data.grassland.share_burnt
        # * (
        #  self.land_use_data.grassland.share_organic
        # + self.land_use_data.grassland.share_organic_mineral
        # )
        # )
        # * ef_wildfire_MB_time_CF_wet_organic_soil_grassland
        # * ef_wildfire_GEF_co2_wet
        # * 10**-3
        # )
        fire_drained_organic_soil = (
            (
                self.land_use_data.grassland.area_ha
                * self.land_use_data.grassland.share_burnt
                * self.land_use_data.grassland.share_organic
            )
            * ef_wildfire_MB_time_CF_drained_organic_soil_grassland
            * ef_wildfire_GEF_co2_drained
            * 10**-3
        )

        # return (
        # fire_mineral_soil + fire_undrained_organic_soil + fire_drained_organic_soil
        # )
        return fire_mineral_soil + fire_drained_organic_soil

    def burning_ch4_grassland(self):
        """
        𝐿𝑓𝑖𝑟𝑒 = 𝐴 ∙ 𝑀𝐵 ∙ 𝐶𝑓 ∙ 𝐺𝑒𝑓 ∙ 10^−3

        For Cf (Combustion factor), it is assumed that all the available fuel is burned,
        thus the value used is 1.0.

        """

        ef_wildfire_MB_time_CF_mineral_soil_grassland = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_wildfire_GEF_ch4_mineral_soil_grassland"
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
                self.land_use_data.grassland.area_ha
                * self.land_use_data.grassland.share_mineral
                * self.land_use_data.grassland.share_burnt
            )
            * ef_wildfire_MB_time_CF_mineral_soil_grassland
            * ef_wildfire_GEF_ch4_mineral
            * 10**-3
        )
        # fire_undrained_organic_soil = (
        # (
        # self.land_use_data.grassland.area_ha
        # * self.land_use_data.grassland.share_burnt
        # * (
        # self.land_use_data.grassland.share_organic
        # + self.land_use_data.grassland.share_organic_mineral
        # )
        # )
        # * ef_wildfire_MB_time_CF_wet_organic_soil_grassland
        # * ef_wildfire_GEF_ch4_wet
        # * 10**-3
        # )
        fire_drained_organic_soil = (
            (
                self.land_use_data.grassland.area_ha
                * self.land_use_data.grassland.share_burnt
                * self.land_use_data.grassland.share_organic
            )
            * ef_wildfire_MB_time_CF_drained_organic_soil_grassland
            * ef_wildfire_GEF_ch4_drained
            * 10**-3
        )

        return fire_mineral_soil + fire_drained_organic_soil

    def burning_n2o_grassland(self):

        """
        For Cf (Combustion factor), it is assumed that all the available fuel is burned,
        thus the value used is 1.0.

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
                self.land_use_data.grassland.area_ha
                * self.land_use_data.grassland.share_burnt
                * self.land_use_data.grassland.share_mineral
            )
            * ef_wildfire_MB_time_CF_mineral_soil_grassland
            * ef_wildfire_GEF_n2o_grassland_mineral
            * 10**-3
        )
        # fire_undrained_organic_soil = (
        # (
        # self.land_use_data.grassland.area_ha
        # * self.land_use_data.grassland.share_burnt
        # * (
        # self.land_use_data.grassland.share_organic
        # + self.land_use_data.grassland.share_organic_mineral
        # )
        # )
        # * ef_wildfire_MB_time_CF_wet_organic_soil_grassland
        # * ef_wildfire_GEF_n2o_grassland_wet
        # * 10**-3
        # )

        fire_drained_organic_soil = (
            (
                self.land_use_data.grassland.area_ha
                * self.land_use_data.grassland.share_burnt
                * self.land_use_data.grassland.share_organic
            )
            * ef_wildfire_MB_time_CF_drained_organic_soil_grassland
            * ef_wildfire_GEF_n2o_grassland_drained
            * 10**-3
        )

        return fire_mineral_soil + fire_drained_organic_soil


class Cropland(LandUse):
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
        returns emissions in tonnes
        """
        ef_cropland_fuel_burning = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_cropland_fuel_burning"
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
        ef_cropland_fuel_burning = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_cropland_fuel_burning"
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


class Forest(LandUse):
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

        
        self.drained_forest_area_exclude_over_50 = self.get_valid_area()
        self.forest_drained_area = (
            self.land_use_data.forest.area_ha
            * self.land_use_data.forest.share_organic
        )

    def get_valid_area(self):

        over_50_years = self.forest_age_data.loc[
            (self.forest_age_data["year"] == 51), "aggregate"
        ].values[0]
        valid_area = 1 - over_50_years

        forest_drained_area_valid = (
            self.land_use_data.forest.area_ha * valid_area
        ) * self.land_use_data.forest.share_organic

        return forest_drained_area_valid

    def co2_drainage_organic_soils_forest(self):

        """Proportion drained, if older than 50 years, not emitting"""

        ef_co2_forest_drainage_off_site = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_forest_drainage_off_site"
            )
        )
        ef_co2_forest_drainage_on_site = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_forest_drainage_on_site"
            )
        )

        return (
            ef_co2_forest_drainage_on_site + ef_co2_forest_drainage_off_site
        ) * self.drained_forest_area_exclude_over_50

    def ch4_drainage_organic_soils_forest(self):
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

        share_forest_drainage_rich = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "share_forest_drainage_rich"
            )
        )
        share_forest_drainage_poor = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "share_forest_drainage_poor"
            )
        )

        return (
            (
                ef_ch4_forest_drainage_land * (1.0 - (frac_ditch_poor))
                + (frac_ditch_poor) * ef_ch4_forest_drainage_ditch
            )
            * self.forest_drained_area
            * share_forest_drainage_poor
        ) + (
            (
                ef_ch4_forest_drainage_land * (1.0 - (frac_ditch_rich))
                + (frac_ditch_rich) * ef_ch4_forest_drainage_ditch
            )
            * self.forest_drained_area
            * share_forest_drainage_rich
        )

    def n2o_drainage_organic_soils_forest(self):

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

        share_forest_drainage_rich = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "share_forest_drainage_rich"
            )
        )
        share_forest_drainage_poor = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "share_forest_drainage_poor"
            )
        )

        area_rich = self.forest_drained_area * share_forest_drainage_rich
        area_poor = self.forest_drained_area * share_forest_drainage_poor

        return (area_rich * ef_n2o_forest_drainage_rich) + (
            area_poor * ef_n2o_forest_drainage_poor
        )

    def burning_co2_forest(self):
        ef_forest_fuel_burning = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_forest_fuel_burning"
            )
        )
        ef_co2_forest_Gef = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_co2_forest_Gef"
            )
        )

        combustion_factor = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_forest_Cf"
            )
        )

        return (
            (self.land_use_data.forest.area_ha * self.land_use_data.forest.share_burnt)
            * ef_forest_fuel_burning
            * combustion_factor
            * ef_co2_forest_Gef
            * 10**-3
        )

    def burning_ch4_forest(self):
        ef_forest_fuel_burning = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_forest_fuel_burning"
            )
        )
        ef_ch4_forest_Gef = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_ch4_forest_Gef"
            )
        )

        combustion_factor = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_forest_Cf"
            )
        )

        return (
            (self.land_use_data.forest.area_ha * self.land_use_data.forest.share_burnt)
            * ef_forest_fuel_burning
            * combustion_factor
            * ef_ch4_forest_Gef
            * 10**-3
        )

    def burning_n2o_forest(self):
        ef_forest_fuel_burning = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_forest_fuel_burning"
            )
        )
        ef_n2o_forest_Gef = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_n2o_forest_Gef"
            )
        )

        combustion_factor = (
            self.emissions_factors.get_emission_factor_in_emission_factor_data_base(
                "ef_forest_Cf"
            )
        )

        return (
            (self.land_use_data.forest.area_ha * self.land_use_data.forest.share_burnt)
            * ef_forest_fuel_burning
            * combustion_factor
            * ef_n2o_forest_Gef
            * 10**-3
        )


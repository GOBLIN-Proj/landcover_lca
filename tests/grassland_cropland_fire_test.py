"""FIRE-2: grassland and cropland fire follow NID 2026 Tier 1.

- Grassland (NID 2026 s.6.5.4, Table 6.34): CH4 and N2O only. "In the Tier 1 methodology, there are no long-term losses
  of biomass carbon due to fires on grassland, and emissions are estimated for CH4 and N2O only." The package keeps the
  CO2 calculation (Table 6.34 Gef CO2) behind include_fire_co2=False, so grassland fire CO2 is 0 unless asked for.
- Cropland (NID 2026 s.6.4.8): CH4 and N2O only, MB.Cf 4.0 t/ha, Gef CH4 2.7, N2O 0.07 g/kg dry matter.
- The burnt share applies equally to every grassland soil type (mineral, drained and undrained organic).
"""
import unittest

import inventory_inputs as ii
import landcover_lca.lca_emission as lca
import landcover_lca.geo_goblin.geo_lca_emissions as geo_lca
import landcover_lca.geo_goblin.geo_models as geo_models
from landcover_lca.models import Emissions_Factors, load_land_use_data

TABLE_6_34 = {  # (mineral, drained organic, undrained organic), as published (organic-soil CO2 is g CO2-C per kg DM)
    "MB_time_CF": (("ef_wildfire_MB_time_CF_mineral_soil_grassland", 4.1),
                   ("ef_wildfire_MB_time_CF_drained_organic_soil_grassland", 336.0),
                   ("ef_wildfire_MB_time_CF_wet_organic_soil_grassland", 66.0)),
    "CO2": (("ef_wildfire_GEF_co2_mineral_soil_grassland", 1613.0),
            ("ef_wildfire_GEF_co2_drained_organic_soil_grassland", 362.0),
            ("ef_wildfire_GEF_co2_wet_organic_soil_grassland", 362.0)),
    "CH4": (("ef_wildfire_GEF_ch4_mineral_soil_grassland", 2.3),
            ("ef_wildfire_GEF_ch4_drained_in_organic_grassland", 9.0),
            ("ef_wildfire_GEF_ch4_wet_in_organic_soil_grassland", 9.0)),
    "N2O": (("ef_wildfire_GEF_n2o_mineral_soil_grassland", 0.21),
            ("ef_wildfire_GEF_n2o_drained_in_organic_grassland", 0.21),
            ("ef_wildfire_GEF_n2o_wet_in_organic_grassland", 0.21)),
}
CROPLAND = (("ef_wildfire_MB_time_CF_cropland", 4.0), ("ef_ch4_cropland_Gef", 2.7), ("ef_n2o_cropland_Gef", 0.07))

YEAR = 2020  # an inventory year with burnt area on every land use


def inputs():
    return ii.inventory_inputs(YEAR)


def geo_inputs():
    """The same inventory inputs in the geo_goblin schema. Its grassland reads drained organic from share_organic +
    share_organic_mineral and rewetted from share_rewetted_in_organic + share_rewetted_in_organic_mineral."""
    f = ii.inventory_land_use_frame(YEAR)
    grass = f.land_use == "grassland"
    geo = f[["farm_id", "year", "land_use", "area_ha", "share_mineral", "share_rewetted_in_mineral", "share_burnt"]].copy()
    geo["share_organic"] = f.share_organic
    geo["share_organic_mineral"] = f.share_organic_mineral
    geo["share_rewetted_in_organic"] = f.share_rewetted_in_organic
    geo["share_rewetted_in_organic_mineral"] = 0.0
    geo["share_peat_extraction"] = 0.0
    geo.loc[grass, "share_organic"] = f.share_drained_rich_organic[grass]
    geo.loc[grass, "share_organic_mineral"] = f.share_drained_poor_organic[grass]
    geo.loc[grass, "share_rewetted_in_organic"] = f.share_rewetted_poor_organic[grass]
    geo.loc[grass, "share_rewetted_in_organic_mineral"] = f.share_rewetted_rich_organic[grass]
    data = geo_models.load_land_use_data(geo, YEAR)
    tm = geo_models.load_transition_matrix(ii.inventory_transition_frame(YEAR, f), "ireland", YEAR, YEAR)
    return data[-YEAR], data[-YEAR], tm[-YEAR]


class TestFactorsAreTheNid(unittest.TestCase):
    def test_grassland_table_6_34(self):
        ef = Emissions_Factors("ireland")
        for group, cells in TABLE_6_34.items():
            for name, value in cells:
                with self.subTest(name=name):
                    self.assertEqual(ef.get_published_factor(name)[0], value)

    def test_cropland_s_6_4_8(self):
        ef = Emissions_Factors("ireland")
        for name, value in CROPLAND:
            with self.subTest(name=name):
                self.assertEqual(ef.get_published_factor(name)[0], value)


class TestGrasslandFireCo2(unittest.TestCase):
    def test_zero_by_default(self):
        land_use, past, tm = inputs()
        self.assertGreater(land_use.grassland.share_burnt, 0)
        self.assertEqual(lca.burning_co2_grassland("ireland", tm, land_use, past), 0)
        geo_land_use, geo_past, geo_tm = geo_inputs()
        self.assertEqual(geo_lca.burning_co2_grassland("ireland", geo_tm, geo_land_use, geo_past), 0)

    def test_total_is_unchanged_by_burnt_area(self):
        land_use, past, tm = inputs()
        frame = ii.inventory_land_use_frame(YEAR)
        frame.loc[frame.land_use == "grassland", "share_burnt"] = 0.0
        unburnt = load_land_use_data(frame, YEAR)[-YEAR]
        self.assertEqual(lca.total_co2_emission_grassland(land_use, past, tm, "ireland"),
                         lca.total_co2_emission_grassland(unburnt, unburnt, tm, "ireland"))

    def test_calculation_kept_when_asked_for(self):
        """include_fire_co2=True gives the Tier 1 CO2 (A x MB.Cf x Gef x 1e-3, t), all three soil types."""
        land_use, past, tm = inputs()
        g = land_use.grassland
        burnt = g.area_ha * g.share_burnt
        (_, mb_m), (_, mb_d), (_, mb_w) = TABLE_6_34["MB_time_CF"]
        # Gef in g CO2 per kg DM as the calculation receives it: mineral 1613 g CO2, organic 362 g CO2-C x 44/12
        gef_m, gef_d, gef_w = (ii.factor(name) for name, _ in TABLE_6_34["CO2"])
        self.assertAlmostEqual(gef_d, 362 * 44 / 12, places=9)
        want_t = burnt * 1e-3 * (g.share_mineral * mb_m * gef_m
                                 + (g.share_drained_rich_organic + g.share_drained_poor_organic) * mb_d * gef_d
                                 + (g.share_rewetted_rich_organic + g.share_rewetted_poor_organic) * mb_w * gef_w)
        self.assertGreater(want_t, 0)
        got = lca.burning_co2_grassland("ireland", tm, land_use, past, include_fire_co2=True)
        self.assertAlmostEqual(got / 1000, want_t, places=6)
        geo_land_use, geo_past, geo_tm = geo_inputs()
        got_geo = geo_lca.burning_co2_grassland("ireland", geo_tm, geo_land_use, geo_past, include_fire_co2=True)
        self.assertAlmostEqual(got_geo / 1000, want_t, places=6)


class TestGrasslandFireCh4N2o(unittest.TestCase):
    def test_every_soil_type_is_charged(self):
        """CH4 and N2O: the burnt share applies to mineral, drained and undrained organic soil alike."""
        land_use, past, tm = inputs()
        g = land_use.grassland
        burnt = g.area_ha * g.share_burnt
        mb = [v for _, v in TABLE_6_34["MB_time_CF"]]
        shares = [g.share_mineral, g.share_drained_rich_organic + g.share_drained_poor_organic,
                  g.share_rewetted_rich_organic + g.share_rewetted_poor_organic]
        for gas, function in (("CH4", lca.burning_ch4_grassland), ("N2O", lca.burning_n2o_grassland)):
            with self.subTest(gas=gas):
                gef = [v for _, v in TABLE_6_34[gas]]
                want_kg = burnt * sum(s * m * e for s, m, e in zip(shares, mb, gef))  # t x 1e-3 x 1000 kg
                self.assertAlmostEqual(function("ireland", tm, land_use, past), want_kg, places=3)


if __name__ == "__main__":
    unittest.main()

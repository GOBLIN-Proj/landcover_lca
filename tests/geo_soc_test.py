"""D8: the geo tree shares the national tree's mineral-soil SOC code (option C).

geo_goblin/land_classes/soc.py re-exports landcover_lca.land_classes.soc.SOC, and geo_lca_emissions imports the
mineral-soil CO2 and N2O functions from lca_emission, so the D1-D6 fixes apply to both trees and stay in step.
Before D8 the geo copy returned None for spans of 20 years or less (D1), returned t C as kg CO2 (D2), raised a bare
KeyError for a missing transition (D3), used SOCref 73.51 for cropland transitions instead of LAC 85 (D4a), charged
N2O as C x 1/15 only (D5) and did not check the years (D6).

Run on the geo test data (geo_data/) with geo_models, as geo_goblin calls it.
"""
import unittest

import pandas as pd

import landcover_lca.lca_emission as lca
import landcover_lca.geo_goblin.geo_lca_emissions as geo_lca
from landcover_lca.geo_goblin.geo_models import load_land_use_data, load_transition_matrix
from landcover_lca.geo_goblin.land_classes.soc import SOC as GeoSOC
from landcover_lca.land_classes.soc import SOC
from soc_test import expected

C_TO_CO2 = 44 / 12
TRANSITION = pd.read_csv("./geo_data/transition_matrix.csv", index_col=0)
LAND_USE = pd.read_csv("./geo_data/land_uses.csv", index_col=0)
SHARED = (
    "mineral_soils_co2_from_cropland_to_forest", "mineral_soils_co2_from_cropland_to_grassland",
    "mineral_soils_co2_from_forest_to_cropland", "mineral_soils_co2_from_forest_to_grassland",
    "mineral_soils_co2_from_forest_to_settlement", "mineral_soils_co2_from_grassland_to_cropland",
    "mineral_soils_co2_from_grassland_to_forest", "mineral_soils_co2_to_forest",
    "mineral_soils_n2o_from_forest_to_grassland", "n2o_from_soil_carbon_loss",
)
# Not shared: grassland remaining grassland goes through the Grassland class, which reads the geo land-use columns.


def geo_run(column, func, span, area=1000.0):
    target = 2020 + span
    lu = LAND_USE.copy()
    lu.loc[lu.year == 2050, "year"] = target
    t = TRANSITION.copy()
    t.loc[0, :] = 0.0
    t.loc[0, column] = area
    tm = load_transition_matrix(t, "ireland", 2020, target)
    ld = load_land_use_data(lu, 2020)
    return func(ld[0], ld[-2020], tm[0], "ireland")


class TestShared(unittest.TestCase):
    def test_soc_class_is_the_national_one(self):
        self.assertIs(GeoSOC, SOC)

    def test_functions_are_the_national_ones(self):
        for name in SHARED:
            with self.subTest(function=name):
                self.assertIs(getattr(geo_lca, name), getattr(lca, name))

    def test_misspelled_name_is_gone(self):
        self.assertFalse(hasattr(geo_lca, "mineral_soils_co2_grassland_remainging_grassland"))
        self.assertTrue(callable(geo_lca.mineral_soils_co2_grassland_remaining_grassland))


class TestGeoResults(unittest.TestCase):
    def test_grassland_to_cropland_kg_co2_every_span(self):
        # Before D8, 30 years: 1102.65 (t C, read as kg CO2; SOCref 73.51). After: 4,675,000 kg CO2.
        for span in (5, 20, 30):
            with self.subTest(span=span):
                got = geo_run("Grassland_to_Cropland", geo_lca.mineral_soils_co2_from_grassland_to_cropland, span)
                self.assertAlmostEqual(got, expected("grassland", "cropland", span) * 1000 * C_TO_CO2, places=3)

    def test_cropland_total_includes_it(self):
        base = geo_run("Grassland_to_Cropland", geo_lca.total_co2_emission_cropland, 30, area=0.0)
        got = geo_run("Grassland_to_Cropland", geo_lca.total_co2_emission_cropland, 30)
        self.assertAlmostEqual(got - base, 4675000.0, places=3)

    def test_forest_to_grassland_n2o_full_chain(self):
        # N2O = C loss (t) x 1/15 x 1000 x (EF1 0.006 + FracLEACH 0.1 x EF5 0.011) x 44/28 (NID 2026 s.6.11; D5)
        c_loss = expected("forest", "grassland", 30)
        want = c_loss / 15 * 1000 * (0.006 + 0.1 * 0.011) * 44 / 28
        got = geo_run("Forest_to_Grassland", geo_lca.mineral_soils_n2o_from_forest_to_grassland, 30)
        self.assertAlmostEqual(got, want, places=6)

    def test_short_span_gives_a_number(self):
        self.assertIsNotNone(geo_run("Grassland_to_Cropland", geo_lca.mineral_soils_co2_from_grassland_to_cropland, 10))

    def test_missing_transition_column_names_it(self):
        t = TRANSITION.drop(columns=["Grassland_to_Cropland"])
        tm = load_transition_matrix(t, "ireland", 2020, 2050)
        ld = load_land_use_data(LAND_USE, 2020)
        with self.assertRaises(KeyError) as cm:
            geo_lca.mineral_soils_co2_from_grassland_to_cropland(ld[0], ld[-2020], tm[0], "ireland")
        self.assertIn("grassland_to_cropland", str(cm.exception))



class TestGeoTotalsOnGeoData(unittest.TestCase):
    def test_totals_unchanged(self):
        # The geo test data converts only grassland to forest, which is not in the totals (CBM covers forest soils),
        # so D8 leaves them unchanged (kg). F6 (forest drainage CO2) moved CO2 by -18,583,840 kg in each dataset: the
        # geo test forest is mostly organo-mineral (12,393 ha against 2,371 ha organic), so SD 0.933 -> 0.581
        # outweighs removing the 50-year cut-off. CO2 before F6: 133971826.04683049, 122629401.79768224,
        # 145660669.08654857.
        tm = load_transition_matrix(TRANSITION, "ireland", 2020, 2050)
        ld = load_land_use_data(LAND_USE, 2020)
        pins = {-2020: (115387986.0252926, 850524.8107858208, 57966.33763685918),
                0: (104045561.77614434, 1260910.4460398883, 57948.86355070993),
                1: (127076829.06501068, 2285026.350583825, 57860.04917144225)}
        for k, want in pins.items():
            for function, value in zip((geo_lca.total_co2_emission, geo_lca.total_ch4_emission,
                                        geo_lca.total_n2o_emission), want):
                with self.subTest(dataset=k, function=function.__name__):
                    self.assertAlmostEqual(function(ld[k], ld[-2020], tm[k], "ireland"), value, delta=1e-3)

if __name__ == "__main__":
    unittest.main()

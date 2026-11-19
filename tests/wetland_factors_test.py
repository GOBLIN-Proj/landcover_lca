"""WET: wetland factors and the restored-wetland biomass removal.

- Rewetted CH4: one factor per peat category, because no rich/poor area split is published.
  Industrial 216 kg CH4/ha (NID 2026 s.6.6.4.2, nutrient rich, as the NID applies it); domestic 106.4 kg CH4/ha,
  the CRT 2026 4(II) "Other Domestic Peat Extraction" implied factor, a weighted average of the NID's 216 (rich)
  and 92 (poor) kg CH4/ha (about 12% rich). Each is applied to its own area.
- Domestic drained and near-natural wetland reproduce the CRT exactly on the inventory areas.
- Fire: the CRT CO2/CH4 and N2O/CH4 ratios equal the package's Gef ratios in every year.
- co2_removals (W1/W3, main and geo_goblin): removal in the target year = annual area x min(span, 5) x factor / 5
  (NID: 0.6 t C/ha/yr for 5 years after rewetting; factor -3 t C/ha).
"""
import math
import unittest

import inventory_inputs as ii
import landcover_lca.lca_emission as lca
import landcover_lca.models as models
import landcover_lca.geo_goblin.geo_models as geo_models
from landcover_lca.land_classes.wetland import Wetland
from landcover_lca.geo_goblin.land_classes.wetland import Wetland as GeoWetland

EF = models.Emissions_Factors("ireland")


class TestRewettedCH4Factors(unittest.TestCase):
    def test_published_values(self):
        self.assertEqual(EF.get_published_factor("ef_ch4_wetland_rewet_industrial"), (216.0, "kg CH4/ha/yr"))
        self.assertEqual(EF.get_published_factor("ef_ch4_wetland_rewet_domestic"), (106.4, "kg CH4/ha/yr"))

    def test_domestic_is_a_weighted_average_of_the_nid_values(self):
        rich = (106.4 - 92.0) / (216.0 - 92.0)
        self.assertTrue(0 < rich < 1)
        self.assertAlmostEqual(rich, 0.116, places=3)

    def test_domestic_equals_the_crt_implied_factor_every_year(self):
        for year in ii.YEARS:
            with self.subTest(year=year):
                self.assertAlmostEqual(ii.crt(year, "II.D.other_domestic", "ief_ch4"), 106.4, places=9)

    def test_misspelled_columns_are_gone(self):
        for old in ("ef_ch4_wetland_rewet_off_site_deafult", "ef_co2_wetland_rewet_off_site_deafult"):
            with self.assertRaises(KeyError):
                EF.get_emission_factor_in_emission_factor_data_base(old)

    def test_each_factor_is_applied_to_its_own_area(self):
        for year in ii.YEARS:
            with self.subTest(year=year):
                got = ii.run(lca.rewetting_ch4_organic_soils_in_wetland, year)
                want = (ii.crt(year, "II.D.other_domestic", "area") * ii.KHA * 106.4
                        + ii.crt(year, "II.D.rewetted_industrial", "area") * ii.KHA * 216.0)
                self.assertAlmostEqual(got / want, 1.0, places=12)

    def test_domestic_rewetted_ch4_equals_the_crt(self):
        for year in ii.YEARS:
            with self.subTest(year=year):
                got = ii.crt(year, "II.D.other_domestic", "area") * ii.KHA * \
                    EF.get_emission_factor_in_emission_factor_data_base("ef_ch4_wetland_rewet_domestic") / 1e6
                self.assertAlmostEqual(got, ii.crt(year, "II.D.other_domestic", "CH4"), places=6)


class TestDomesticAndNearNaturalMatchTheCRT(unittest.TestCase):
    def test_domestic_drained(self):
        get = EF.get_emission_factor_in_emission_factor_data_base
        for year in ii.YEARS:
            area = ii.crt(year, "II.D.domestic", "area") * ii.KHA
            with self.subTest(year=year):
                self.assertAlmostEqual(area * get("ef_co2_wetland_domestic_extraction_on_site") / 1e6,
                                       -ii.crt(year, "D.domestic", "organic_soil_C") * ii.C_TO_CO2, places=6)
                self.assertAlmostEqual(area * get("ef_co2_wetland_drainage_DOC_default") / 1e6,
                                       ii.crt(year, "II.D.domestic", "CO2"), places=6)
                frac = get("frac_ditch")
                ch4 = (1 - frac) * get("ef_ch4_wetland_drainage_land_default") + frac * get(
                    "ef_ch4_wetland_drainage_ditch_default")
                self.assertAlmostEqual(area * ch4 / 1e6, ii.crt(year, "II.D.domestic", "CH4"), places=6)

    def test_near_natural(self):
        get = EF.get_emission_factor_in_emission_factor_data_base
        for year in ii.YEARS:
            area = ii.crt(year, "II.D.near_natural", "area") * ii.KHA
            with self.subTest(year=year):
                self.assertAlmostEqual(area * get("ef_co2_near_natural_wetland_runoff") / 1e6,
                                       ii.crt(year, "II.D.near_natural", "CO2"), places=6)
                self.assertAlmostEqual(area * get("ef_ch4_near_natural_wetland") / 1e6,
                                       ii.crt(year, "II.D.near_natural", "CH4"), places=6)


class TestFireRatios(unittest.TestCase):
    def test_gef_ratios_equal_the_crt(self):
        get = EF.get_emission_factor_in_emission_factor_data_base
        co2, ch4, n2o = get("ef_co2_wetland_Gef"), get("ef_ch4_wetland_Gef"), get("ef_n2o_wetland_Gef")
        for year in ii.YEARS:
            with self.subTest(year=year):
                c = ii.crt(year, "IV.D.1", "CH4")
                self.assertAlmostEqual(ii.crt(year, "IV.D.1", "CO2") / c, co2 / ch4, places=6)
                self.assertAlmostEqual(ii.crt(year, "IV.D.1", "N2O") / c, n2o / ch4, places=9)


def _removal(cls, factors, annual_area, span):
    w = cls.__new__(cls)  # only the attributes co2_removals reads
    w.emissions_factors, w.annual_area, w.year_range = factors, annual_area, span
    return w.co2_removals()


class TestCO2Removals(unittest.TestCase):
    TREES = ((Wetland, models.Emissions_Factors("ireland")), (GeoWetland, geo_models.Emissions_Factors("ireland")))

    def test_factor(self):
        self.assertEqual(EF.get_published_factor("ef_co2_peatland_to_wetland_biomass"), (-3.0, "t C/ha"))

    def test_removal_in_the_target_year(self):
        per_ha_year = -3.0 * 1000 * 44 / 12 / 5  # 0.6 t C/ha/yr for 5 years
        for cls, factors in self.TREES:
            for span, years_counted in ((1, 1), (3, 3), (5, 5), (10, 5), (30, 5)):
                with self.subTest(tree=cls.__module__, span=span):
                    self.assertTrue(math.isclose(_removal(cls, factors, 100.0, span),
                                                 100.0 * years_counted * per_ha_year, rel_tol=1e-12))

    def test_zero_span_or_area_gives_zero(self):
        for cls, factors in self.TREES:
            with self.subTest(tree=cls.__module__):
                self.assertEqual(_removal(cls, factors, 0.0, 0), 0.0)
                self.assertEqual(_removal(cls, factors, 0.0, 10), 0.0)

    def test_negative_span_raises(self):
        for cls, factors in self.TREES:
            with self.subTest(tree=cls.__module__):
                with self.assertRaises(ValueError):
                    _removal(cls, factors, 100.0, -5)


class TestGoblinLiteNationalCH4(unittest.TestCase):
    def test_national_ch4(self):
        # WET (rewetted domestic 216 -> 106.4 kg CH4/ha): before 141999544.9, 125998807.5, 125998799.6 kg.
        # The baseline fall (-9.68 kt) is mostly the input: goblin_lite's 2020 rewetted domestic area equals the
        # drained domestic area (88.3 kha; landcover_assignment, see artifacts/todo/other-packages.md).
        from soc_test import LAND_USE, TRANSITION
        tm = models.load_transition_matrix(TRANSITION, "ireland", 2020, 2050)
        ld = models.load_land_use_data(LAND_USE, 2020)
        for k, want in ((-2020, 132321838.0), (0, 124438595.2), (1, 124438587.3)):
            with self.subTest(scenario=k):
                self.assertAlmostEqual(lca.total_ch4_emission(ld[k], ld[-2020], tm[k], "ireland"), want, delta=0.1)


if __name__ == "__main__":
    unittest.main()

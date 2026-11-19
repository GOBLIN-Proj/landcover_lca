"""P1: horticultural peat, off-site CO2 (NID 2026 s.6.6.3 p.279, s.6.6.4.2 p.280).

- Tonnage used = exports / 0.85: 85% of horticultural peat is exported, and the NID scales the export figures up to
  include domestic use. Exports are UN Comtrade (HS 2703, reporter Ireland, partner world), as the CSO data the NID uses.
- CO2 = tonnage x 0.45 t C/t air-dry peat (IPCC 2006 Vol 4 Table 7.5, nutrient poor; eq 7.5) x 44/12.
- Years in the table use that year. Years after the table use the mean of its last three years. Years before it raise.
- In the national (main-tree) wetland total, which goblin_lite uses, for the year the land-use data carries. Not in the
  geo_goblin total: a national export figure cannot be split to farms or catchments.
- CRT 2026 check: 4.D industrial organic-soil C = 1.7 t C/ha x 4(II) industrial area + 0.45 x exports / 0.85 (exact,
  2020-2024); run in inventory_alignment_test (row wetland_drainage_co2).
"""
import unittest

import landcover_lca.lca_emission as lca
import landcover_lca.models as models
import landcover_lca.geo_goblin.geo_lca_emissions as geo_lca
from landcover_lca.resource_manager.data_loader import Loader

EF = models.Emissions_Factors("ireland")
C_TO_CO2 = 44 / 12

# UN_comtrade_exported_peat, kg. 2011-2022 as before P1. 2023, 2024 added in P1 (Comtrade, fetched 2026-11-19); they
# are the values the CRT 2026 implies. Comtrade has since revised 2021 (589.2 kt) and 2022 (401.6 kt); the CRT 2026
# used the values below, so they are kept.
EXPORTS_KG = {
    2011: 800594790, 2012: 784609773, 2013: 781426387, 2014: 861215775, 2015: 985900330, 2016: 1012633621,
    2017: 836946614, 2018: 765784658, 2019: 791370420, 2020: 919370739, 2021: 579573070, 2022: 390375500,
    2023: 348444751, 2024: 313382351,
}


def co2_kg(exports_kg):
    return exports_kg / 0.85 * 0.45 * C_TO_CO2


class TestData(unittest.TestCase):
    def test_factors(self):
        self.assertEqual(EF.get_published_factor("frac_horticultural_peat_exported"), (0.85, "fraction"))
        self.assertEqual(EF.get_published_factor("ef_offsite_carbon_conversion_nutrient_poor"),
                         (0.45, "t C/t air-dry peat"))

    def test_export_table(self):
        table = Loader("ireland").exported_peat()["Total_kg"]
        self.assertEqual({int(y): int(v) for y, v in table.items()}, EXPORTS_KG)


class TestPeatExportCO2(unittest.TestCase):
    def test_years_in_the_table(self):
        for year, kg in EXPORTS_KG.items():
            with self.subTest(year=year):
                self.assertAlmostEqual(lca.horticulture_co2_peat_export("ireland", year) / co2_kg(kg), 1.0, places=12)

    def test_crt_years_kt(self):
        # kt CO2 off-site: 2020 1784.7, 2024 608.3
        self.assertAlmostEqual(lca.horticulture_co2_peat_export("ireland", 2020) / 1e6, 1784.66, places=2)
        self.assertAlmostEqual(lca.horticulture_co2_peat_export("ireland", 2024) / 1e6, 608.33, places=2)

    def test_years_after_the_table_use_the_last_three_years(self):
        want = co2_kg((EXPORTS_KG[2022] + EXPORTS_KG[2023] + EXPORTS_KG[2024]) / 3)
        for year in (2025, 2030, 2050):
            with self.subTest(year=year):
                self.assertAlmostEqual(lca.horticulture_co2_peat_export("ireland", year) / want, 1.0, places=12)
        self.assertAlmostEqual(want / 1e6, 680.84, places=2)

    def test_years_before_the_table_raise(self):
        with self.assertRaises(ValueError) as cm:
            lca.horticulture_co2_peat_export("ireland", 2010)
        self.assertIn("2011-2024", str(cm.exception))

    def test_calibration_year_no_longer_changes_the_result(self):
        # Kept so three-argument calls still work; the table decides which years are data.
        self.assertEqual(lca.horticulture_co2_peat_export("ireland", 2024, 2020),
                         lca.horticulture_co2_peat_export("ireland", 2024))


class TestTotals(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from soc_test import LAND_USE, TRANSITION
        cls.tm = models.load_transition_matrix(TRANSITION, "ireland", 2020, 2050)
        cls.ld = models.load_land_use_data(LAND_USE, 2020)

    def _parts(self, k):
        ld, past, tm = self.ld[k], self.ld[-2020], self.tm[k]
        return (lca.drainage_co2_organic_soils_in_wetland(ld, past, tm, "ireland")
                + lca.biomass_co2_from_removals_wetland(ld, past, tm, "ireland")
                + lca.burning_co2_wetland("ireland", tm, ld, past)
                + lca.rewetting_co2_organic_soils_in_wetland("ireland", tm, ld, past))

    def test_national_wetland_total_includes_peat_export_for_the_land_use_year(self):
        for k, year in ((-2020, 2020), (0, 2050), (1, 2050)):
            with self.subTest(scenario=k):
                self.assertEqual(self.ld[k].wetland.year, year)
                total = lca.total_co2_emission_wetland(self.ld[k], self.ld[-2020], self.tm[k], "ireland")
                self.assertAlmostEqual(total - self._parts(k), lca.horticulture_co2_peat_export("ireland", year),
                                       delta=1e-3)

    def test_geo_tree_has_no_peat_export(self):
        self.assertFalse(hasattr(geo_lca, "horticulture_co2_peat_export"))


if __name__ == "__main__":
    unittest.main()

"""F6: forest drainage CO2 as the NID calculates it (NID 2026 s.6.3, eq 6.3.2-6.3.4, Tables 6.7 and 6.15).

    CO2 (t C) = A_organic x (1.68 + 0.31) + A_organo-mineral x (1.68 x SD + 0.31)

- A: drained organic (N-poor) and organo-mineral (N-rich) forest areas, the same areas CH4 and N2O use.
  No age cut-off: the NID applies the factors "to all forest over the entire time series regardless of forest age"
  (p.216). Before F6 the package removed forest over 50 years old (8.1%) from the CO2 area only.
- 1.68 t C/ha/yr on-site (eq 6.3.2), 0.31 t C/ha/yr DOC on both soils (p.216).
- SD = depth / 30 cm for organo-mineral soils (eq 6.3.3-6.3.4). The NID text gives no depth; its tables do:
  organo-mineral on-site / (area x 1.68), 4.A.1 + 4.A.2 pooled, 2020-2023 = 381.0 kt C / (390.5 kha x 1.68)
  = 0.5808 (17.4 cm). Before F6 the package used 28 cm (SD 0.933).
The two old errors nearly cancelled (package/CRT 0.994-0.995); after F6 the CRT is reproduced (row
forest_drainage_co2 in inventory_alignment_test, tolerance 0.001).
"""
import csv
import unittest

import landcover_lca.lca_emission as lca
import landcover_lca.models as models
import landcover_lca.geo_goblin.geo_models as geo_models
from landcover_lca.land_classes.forestland import Forest
from landcover_lca.geo_goblin.land_classes.forestland import Forest as GeoForest

EF = models.Emissions_Factors("ireland")
KG_CO2_PER_T_C = 1000 * 44 / 12
NID = [r for r in csv.DictReader(open("./data/inventory/nid2026_forest_organic_soils.csv"))
       if 2020 <= int(r["year"]) <= 2023]


class TestFactors(unittest.TestCase):
    def test_published(self):
        self.assertEqual(EF.get_published_factor("sd_forest_organo_mineral"), (0.581, "fraction"))
        self.assertEqual(EF.get_published_factor("ef_co2_forest_drainage_on_site"), (1.68, "t CO2-C/ha/yr"))
        self.assertEqual(EF.get_published_factor("ef_co2_forest_drainage_off_site_DOC"), (0.31, "t CO2-C/ha/yr"))

    def test_sd_is_what_the_nid_tables_imply(self):
        on_site = sum(-float(r["onsite_organo_mineral_ktC"]) for r in NID)
        area = sum(float(r["drained_organo_mineral_rich_kha"]) for r in NID)
        self.assertAlmostEqual(on_site, 381.0, places=1)
        self.assertAlmostEqual(area, 390.5, places=1)
        self.assertAlmostEqual(on_site / (area * 1.68), 0.581, places=3)

    def test_nid_tables_use_1_68_and_0_31_on_the_full_drained_area(self):
        for r in NID:
            with self.subTest(category=r["category"], year=r["year"]):
                poor, rich = float(r["drained_organic_poor_kha"]), float(r["drained_organo_mineral_rich_kha"])
                self.assertAlmostEqual(-float(r["onsite_organic_ktC"]) / poor, 1.68, delta=0.002)
                self.assertAlmostEqual(-float(r["doc_organic_ktC"]) / poor, 0.31, delta=0.002)
                self.assertAlmostEqual(-float(r["doc_organo_mineral_ktC"]) / rich, 0.31, delta=0.004)


def _forest(cls, poor_ha, rich_ha):
    f = cls.__new__(cls)  # only the attributes the CO2 method reads
    f.emissions_factors = (models if cls is Forest else geo_models).Emissions_Factors("ireland")
    f.forest_poor_drained_area, f.forest_rich_drained_area = poor_ha, rich_ha
    return f


class TestCO2(unittest.TestCase):
    def test_formula_both_trees(self):
        want = (1000 * (1.68 + 0.31) + 500 * (1.68 * 0.581 + 0.31)) * KG_CO2_PER_T_C
        self.assertAlmostEqual(want, 9654480.0, places=3)  # the docstring example
        for cls in (Forest, GeoForest):
            with self.subTest(tree=cls.__module__):
                self.assertAlmostEqual(_forest(cls, 1000.0, 500.0).co2_drainage_organic_soils_forest(), want, places=6)

    def test_no_age_cut_off(self):
        for cls in (Forest, GeoForest):
            with self.subTest(tree=cls.__module__):
                self.assertFalse(hasattr(cls, "get_valid_area"))

    def test_goblin_lite_national(self):
        # before F6: 1,628.9 kt (cut-off 0.919, SD 0.933); after: 1,615.15 kt (poor 174.5 kha, rich 72.5 kha)
        from soc_test import LAND_USE, TRANSITION
        tm = models.load_transition_matrix(TRANSITION, "ireland", 2020, 2050)
        ld = models.load_land_use_data(LAND_USE, 2020)
        for k in (-2020, 0, 1):
            with self.subTest(dataset=k):
                got = lca.organic_soils_co2_forest("ireland", tm[k], ld[k], ld[-2020])
                self.assertAlmostEqual(got / 1e6, (174.5e3 * 1.99 + 72.5e3 * (1.68 * 0.581 + 0.31)) * KG_CO2_PER_T_C / 1e6,
                                       places=6)
                self.assertAlmostEqual(got / 1e6, 1615.15, places=2)


if __name__ == "__main__":
    unittest.main()

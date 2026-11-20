"""FIRE-3: forest fire CO2 is left out of the forest and national CO2 totals by default; include_fire_co2=True adds it.

GOBLIN adds CBM forest carbon ("Total Ecosystem", the change in AGB + BGB + deadwood + litter + soil) to
landcover_lca's forest CO2. cbm_runner simulates fire (DISTID3 = CBM default "Wildfire"), and CBM's disturbance
matrices send the burnt carbon to the atmosphere (CBM-CFS3 v1.2 User's Guide s.1.8.5 p.15, Appendix 6, Table 8-1), so
the fire loss is already in that change. The inventory counts it once: CRT 2026 Table4 4.A = 4.A carbon stock change
+ 4(IV) wildfire CO2, exactly, 2020-2024 (checked below). Without CBM, include_fire_co2=True matches the NID.
CH4 and N2O from forest fire are always included. Both trees; the switch is keyword-only.
"""
import unittest

import pandas as pd

import landcover_lca.lca_emission as lca
import landcover_lca.models as models
import landcover_lca.geo_goblin.geo_lca_emissions as geo_lca
import landcover_lca.geo_goblin.geo_models as geo_models

TREES = ((lca, models, "./goblin_lite_data/transition_matrix.csv", "./goblin_lite_data/landuse_data_test_version.csv"),
         (geo_lca, geo_models, "./geo_data/transition_matrix.csv", "./geo_data/land_uses.csv"))


def load(model, transition, land_use):
    tm = model.load_transition_matrix(pd.read_csv(transition, index_col=0), "ireland", 2020, 2050)
    ld = model.load_land_use_data(pd.read_csv(land_use, index_col=0), 2020)
    return ld, tm


class TestForestFireCO2Switch(unittest.TestCase):
    def test_default_excludes_fire_co2(self):
        # goblin_lite national CO2, 2020: 5,528.7 kt by default; 5,547.2 kt with fire CO2 (the value before the
        # default changed)
        ld, tm = load(*TREES[0][1:])
        args = (ld[-2020], ld[-2020], tm[-2020], "ireland")
        self.assertAlmostEqual(lca.total_co2_emission(*args), 5528697873.1, delta=0.1)
        self.assertAlmostEqual(lca.total_co2_emission(*args, include_fire_co2=True), 5547249730.6, delta=0.1)

    def test_inventory_counts_fire_co2_once(self):
        import inventory_inputs as ii
        for year in ii.YEARS:
            for c in ("1", "2"):
                with self.subTest(year=year, category=c):
                    self.assertAlmostEqual(ii.crt(year, f"T4.A.{c}", "CO2"),
                                           ii.crt(year, f"A.{c}", "net_CO2") + ii.crt(year, f"IV.A.{c}", "CO2"), places=6)

    def test_on_adds_exactly_the_fire_co2(self):
        for module, *data in TREES:
            ld, tm = load(*data)
            for k in (-2020, 0):
                with self.subTest(tree=module.__name__, dataset=k):
                    args = (ld[k], ld[-2020], tm[k], "ireland")
                    fire = module.burning_co2_forest("ireland", tm[k], ld[k], ld[-2020])
                    self.assertGreater(fire, 0)
                    for total in (module.total_co2_emission_forest, module.total_co2_emission):
                        off = total(*args)
                        self.assertEqual(total(*args, include_fire_co2=False), off)
                        self.assertAlmostEqual(total(*args, include_fire_co2=True) - off, fire, delta=1e-6)

    def test_goblin_lite_fire_co2_kt(self):
        ld, tm = load(*TREES[0][1:])
        self.assertAlmostEqual(lca.burning_co2_forest("ireland", tm[-2020], ld[-2020], ld[-2020]) / 1e6, 18.55, places=2)

    def test_ch4_and_n2o_are_not_switched(self):
        for module, *data in TREES:
            with self.subTest(tree=module.__name__):
                for name in ("total_ch4_emission_forest", "total_n2o_emission_forest", "total_ch4_emission",
                             "total_n2o_emission"):
                    self.assertNotIn("include_fire_co2", getattr(module, name).__code__.co_varnames)

    def test_switch_is_keyword_only(self):
        for module, *data in TREES:
            ld, tm = load(*data)
            with self.subTest(tree=module.__name__):
                with self.assertRaises(TypeError):
                    module.total_co2_emission_forest(ld[-2020], ld[-2020], tm[-2020], "ireland", False)


if __name__ == "__main__":
    unittest.main()

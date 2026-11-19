"""FIRE-3: forest fire CO2 can be left out of the forest and national CO2 totals (default: included).

The NID reports forest wildfire CO2 (CRT 4(IV).A), so the default is on and results do not change. The switch is for
a caller that also adds a forest carbon model that may already count the fire carbon loss: goblin_lite adds CBM
"Total Ecosystem" to landcover_lca's forest CO2 (a double count is not confirmed; artifacts/todo/other-packages.md).
CH4 and N2O from forest fire are not switched: CBM does not produce them.
Both trees. The switch is keyword-only.
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
    def test_default_includes_fire_co2(self):
        # goblin_lite national totals unchanged (soc_test pins)
        ld, tm = load(*TREES[0][1:])
        self.assertAlmostEqual(lca.total_co2_emission(ld[-2020], ld[-2020], tm[-2020], "ireland"), 5547249730.6,
                               delta=0.1)

    def test_off_removes_exactly_the_fire_co2(self):
        for module, *data in TREES:
            ld, tm = load(*data)
            for k in (-2020, 0):
                with self.subTest(tree=module.__name__, dataset=k):
                    args = (ld[k], ld[-2020], tm[k], "ireland")
                    fire = module.burning_co2_forest("ireland", tm[k], ld[k], ld[-2020])
                    self.assertGreater(fire, 0)
                    for total in (module.total_co2_emission_forest, module.total_co2_emission):
                        on = total(*args)
                        self.assertEqual(total(*args, include_fire_co2=True), on)
                        self.assertAlmostEqual(on - total(*args, include_fire_co2=False), fire, delta=1e-6)

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

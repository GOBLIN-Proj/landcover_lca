"""The example notebooks run, and give what the packages that use landcover_lca would receive.

- goblin_lite_example.ipynb: national tree (as goblin_lite); totals equal the national pins in soc_test.
- geo_goblin_example.ipynb: geo tree (as geo_goblin); no horticultural peat.
Runs the code cells in order, without Jupyter.
"""
import json
import unittest

import pandas as pd

import landcover_lca.lca_emission as lca


def run_notebook(path):
    with open(path) as f:
        cells = json.load(f)["cells"]
    namespace = {}
    for cell in cells:
        if cell["cell_type"] == "code":
            exec("".join(cell["source"]), namespace)
    return namespace


class TestGoblinLiteExample(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ns = run_notebook("goblin_lite_example.ipynb")

    def test_uses_the_national_tree(self):
        self.assertIs(self.ns["landuse_lca"], lca)

    def test_every_cell_is_filled(self):
        self.assertFalse(self.ns["emissions"].isna().any().any())
        self.assertEqual(len(self.ns["emissions"]), 5 * (1 + len(self.ns["scenarios"])))

    def test_totals_equal_the_national_pins(self):
        e = self.ns["emissions"]["CO2"]
        self.assertAlmostEqual(e[(-1, "total", 2020)], 5547.2497306, places=6)  # before F6: 5561.0290273
        self.assertAlmostEqual(e[(0, "total", 2050)], 5356.2808339, places=6)  # before F6: 5370.0601306
        self.assertAlmostEqual(e[(1, "total", 2050)], 5359.4794831, places=6)  # before F6: 5373.2587798

    def test_land_uses_add_up_to_the_total(self):
        e = self.ns["emissions"]
        for scenario, year in [(-1, 2020)] + [(s, 2050) for s in self.ns["scenarios"]]:
            for gas in ("CO2", "CH4", "N2O"):
                with self.subTest(scenario=scenario, gas=gas):
                    parts = sum(e.loc[(scenario, lu, year), gas] for lu in ("cropland", "grassland", "forest", "wetland"))
                    self.assertAlmostEqual(parts, e.loc[(scenario, "total", year), gas], places=6)


class TestGeoGoblinExample(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ns = run_notebook("geo_goblin_example.ipynb")

    def test_uses_the_geo_tree(self):
        self.assertEqual(self.ns["landuse_lca"].__name__, "landcover_lca.geo_goblin.geo_lca_emissions")
        self.assertFalse(hasattr(self.ns["landuse_lca"], "horticulture_co2_peat_export"))

    def test_every_cell_is_filled(self):
        for name in ("emissions", "eutrophication"):
            with self.subTest(frame=name):
                frame = self.ns[name]
                self.assertIsInstance(frame, pd.DataFrame)
                self.assertFalse(frame.isna().any().any())
        self.assertEqual(len(self.ns["eutrophication"]), 1 + len(self.ns["scenarios"]))


if __name__ == "__main__":
    unittest.main()

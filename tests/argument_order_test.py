"""Every total takes (land_use_data, past_land_use_data, transition_matrix, ef_country), in both trees.

Before, total_ch4_emission_cropland and total_n2o_emission_cropland took (ef_country, transition_matrix, land_use_data,
past_land_use_data). A call in the old order now raises TypeError naming the new order. Values are unchanged.
Settlement totals take (land_use, ef_country) and are not called by any total. Options such as include_fire_co2
(FIRE-3) are keyword-only, so they cannot shift the positional order.
"""
import ast
import inspect
import unittest

import pandas as pd

import landcover_lca.lca_emission as lca
import landcover_lca.models as models
import landcover_lca.geo_goblin.geo_lca_emissions as geo_lca
import landcover_lca.geo_goblin.geo_models as geo_models

ROLES = (("land_use_data", "land_use"), ("past_land_use_data",), ("transition_matrix", "transition_matrix_data"),
         ("ef_country",))
TREES = ((lca, models, "./goblin_lite_data/transition_matrix.csv", "./goblin_lite_data/landuse_data_test_version.csv",
          154.28571428571416, 3.9999999999999964),
         (geo_lca, geo_models, "./geo_data/transition_matrix.csv", "./geo_data/land_uses.csv",
          62.08260266562008, 1.6095489579975577))


def totals(module):
    tree = ast.parse(inspect.getsource(module))
    return [n.name for n in tree.body
            if isinstance(n, ast.FunctionDef) and n.name.startswith("total_") and "settlement" not in n.name]


class TestArgumentOrder(unittest.TestCase):
    def test_every_total_has_the_same_order(self):
        for module, *_ in TREES:
            for name in totals(module):
                with self.subTest(tree=module.__name__, function=name):
                    params = [p for p, v in inspect.signature(getattr(module, name)).parameters.items()
                              if v.kind is not inspect.Parameter.KEYWORD_ONLY]  # keyword-only options allowed
                    self.assertEqual(len(params), 4, params)
                    for param, allowed in zip(params, ROLES):
                        self.assertIn(param, allowed, params)

    def test_cropland_values_unchanged_and_old_order_raises(self):
        for module, model, transition, land_use, ch4, n2o in TREES:
            tm = model.load_transition_matrix(pd.read_csv(transition, index_col=0), "ireland", 2020, 2050)
            ld = model.load_land_use_data(pd.read_csv(land_use, index_col=0), 2020)
            for k in (-2020, 0):
                with self.subTest(tree=module.__name__, dataset=k):
                    self.assertEqual(module.total_ch4_emission_cropland(ld[k], ld[-2020], tm[k], "ireland"), ch4)
                    self.assertEqual(module.total_n2o_emission_cropland(ld[k], ld[-2020], tm[k], "ireland"), n2o)
                    for function in (module.total_ch4_emission_cropland, module.total_n2o_emission_cropland):
                        with self.assertRaises(TypeError) as cm:
                            function("ireland", tm[k], ld[k], ld[-2020])
                        self.assertIn("(land_use_data, past_land_use_data, transition_matrix, ef_country)",
                                      str(cm.exception))


if __name__ == "__main__":
    unittest.main()

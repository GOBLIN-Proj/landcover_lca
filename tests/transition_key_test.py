"""D3: a missing transition-matrix column must raise a clear error, never a bare KeyError (S6).

Run from landcover_lca/tests:  python -m unittest transition_key_test.py
"""
import unittest

import pandas as pd

from landcover_lca.models import load_transition_matrix, load_land_use_data
import landcover_lca.lca_emission as lca

TRANSITION = pd.read_csv("./goblin_lite_data/transition_matrix.csv", index_col=0)
LAND_USE = pd.read_csv("./goblin_lite_data/landuse_data_test_version.csv", index_col=0)

# The 8 columns read by the SOC and land use code (see artifacts/soc/D3-missing-transition-key.md)
REQUIRED = [
    "Grassland_to_Grassland", "Grassland_to_Cropland", "Wetland_to_Wetland",
    "Cropland_to_Grassland", "Cropland_to_Cropland", "Forest_to_Grassland",
    "Forest_to_Cropland", "Forest_to_Forest",
]


def run_total(drop):
    t = TRANSITION.drop(columns=[drop])
    tm = load_transition_matrix(t, "ireland", 2020, 2050)
    ld = load_land_use_data(LAND_USE, 2020)
    for f in (lca.total_co2_emission, lca.total_ch4_emission, lca.total_n2o_emission):
        f(ld[0], ld[-2020], tm[0], "ireland")


class TestMissingTransitionColumn(unittest.TestCase):
    def test_each_required_column_raises_informative_error(self):
        for col in REQUIRED:
            with self.subTest(column=col):
                with self.assertRaises(KeyError) as cm:
                    run_total(col)
                msg = str(cm.exception)
                self.assertIn(col.lower(), msg)
                self.assertIn("transition matrix", msg.lower())
                self.assertIn("available", msg.lower())

    def test_helper_lists_available_columns(self):
        from landcover_lca.models import get_transition_area
        tm = load_transition_matrix(TRANSITION.drop(columns=["Forest_to_Cropland"]), "ireland", 2020, 2050)
        with self.assertRaises(KeyError) as cm:
            get_transition_area(tm[0], "forest", "cropland")
        self.assertIn("grassland_to_cropland", str(cm.exception))

    def test_present_column_unchanged(self):
        from landcover_lca.models import get_transition_area
        tm = load_transition_matrix(TRANSITION, "ireland", 2020, 2050)
        self.assertEqual(get_transition_area(tm[0], "grassland", "grassland"),
                         tm[0].__dict__["grassland_to_grassland"])

    def test_column_not_required_missing_is_harmless(self):
        # Settlement columns are never read: dropping one must not change the result.
        full = load_transition_matrix(TRANSITION, "ireland", 2020, 2050)
        less = load_transition_matrix(TRANSITION.drop(columns=["Settlement_to_Forest"]), "ireland", 2020, 2050)
        ld = load_land_use_data(LAND_USE, 2020)
        self.assertEqual(lca.total_co2_emission(ld[0], ld[-2020], full[0], "ireland"),
                         lca.total_co2_emission(ld[0], ld[-2020], less[0], "ireland"))


if __name__ == "__main__":
    unittest.main()

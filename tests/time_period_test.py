"""D6 / S8: the span between the baseline and the evaluated year (year_range) has one implementation and is validated.

Run from landcover_lca/tests:  python -m unittest time_period_test.py

The span is year(current land use, target dataset) - year(current land use, baseline dataset).
It is checked that the source category carries the same year as the destination within each dataset,
and a missing category gives a clear error.
"""
import copy
import unittest

import pandas as pd

from landcover_lca.land_classes.landuse import LandUse
from landcover_lca.land_classes.soc import SOC
from landcover_lca.models import get_time_period, load_land_use_data, load_transition_matrix

TRANSITION = pd.read_csv("./goblin_lite_data/transition_matrix.csv", index_col=0)
LAND_USE = pd.read_csv("./goblin_lite_data/landuse_data_test_version.csv", index_col=0)


def datasets():
    """Fresh copies: scenario 0 (2050) and baseline (2020) land use, and the transition matrix."""
    ld = load_land_use_data(LAND_USE.copy(), 2020)
    tm = load_transition_matrix(TRANSITION.copy(), "ireland", 2020, 2050)
    return copy.deepcopy(ld[0]), copy.deepcopy(ld[-2020]), tm[0]


class TestTimePeriod(unittest.TestCase):
    def test_national_case_is_30_years(self):
        target, past, _ = datasets()
        self.assertEqual(get_time_period(target, past, "grassland", "forest"), 30)
        self.assertEqual(get_time_period(target, past, "cropland"), 30)

    def test_baseline_call_is_zero(self):
        _, past, _ = datasets()
        self.assertEqual(get_time_period(past, past, "grassland", "grassland"), 0)

    def test_soc_and_landuse_use_the_same_value(self):
        target, past, tm = datasets()
        soc = SOC("ireland", target, past, tm, "grassland", "forest")
        lu = LandUse("ireland", tm, target, past, "forest", "grassland")
        self.assertEqual(soc.year_range, 30)
        self.assertEqual(lu.year_range, 30)
        self.assertEqual(soc.get_time_period(), lu.get_time_period())


class TestMissingCategory(unittest.TestCase):
    def test_missing_destination_in_target_dataset(self):
        target, past, _ = datasets()
        del target.__dict__["cropland"]
        with self.assertRaises(KeyError) as cm:
            get_time_period(target, past, "cropland", "grassland")
        msg = str(cm.exception)
        self.assertIn("land_use_data", msg)
        self.assertIn("cropland", msg)
        self.assertIn("grassland", msg)  # lists what is available

    def test_missing_destination_in_past_dataset(self):
        target, past, _ = datasets()
        del past.__dict__["cropland"]
        with self.assertRaises(KeyError) as cm:
            get_time_period(target, past, "cropland", "grassland")
        self.assertIn("past_land_use_data", str(cm.exception))

    def test_missing_source_category_cannot_be_compared_and_is_not_an_error(self):
        target, past, _ = datasets()
        del target.__dict__["forest"]
        self.assertEqual(get_time_period(target, past, "grassland", "forest"), 30)


class TestMixedYears(unittest.TestCase):
    def test_target_dataset_with_different_years_raises(self):
        target, past, _ = datasets()
        target.forest.year = 2045
        with self.assertRaises(ValueError) as cm:
            get_time_period(target, past, "grassland", "forest")
        self.assertIn("land_use_data", str(cm.exception))
        self.assertIn("2045", str(cm.exception))

    def test_past_dataset_with_different_years_raises(self):
        target, past, _ = datasets()
        past.forest.year = 2019
        with self.assertRaises(ValueError) as cm:
            get_time_period(target, past, "grassland", "forest")
        self.assertIn("past_land_use_data", str(cm.exception))

    def test_constructors_raise_too(self):
        target, past, tm = datasets()
        target.forest.year = 2045
        with self.assertRaises(ValueError):
            SOC("ireland", target, past, tm, "grassland", "forest")
        with self.assertRaises(ValueError):
            LandUse("ireland", tm, target, past, "forest", "grassland")

    def test_same_category_never_conflicts(self):
        target, past, _ = datasets()
        target.forest.year = 2045  # irrelevant when forest is not part of the transition
        self.assertEqual(get_time_period(target, past, "grassland", "grassland"), 30)


if __name__ == "__main__":
    unittest.main()

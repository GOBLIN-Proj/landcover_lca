"""The implied emission factors in the database are derived values: each must be reproducible
from the stored CRF extract, and documented in docs/emission_factor_provenance.md.

Run from landcover_lca/tests:  python -m unittest implied_factor_test.py
"""
import os
import sys
import unittest

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))

from landcover_lca.models import Emissions_Factors

CSV = "./data/inventory/crf_4c1_grassland_remaining_mineral.csv"
PROVENANCE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "emission_factor_provenance.md")

# The derivation chosen for ef_co2_implied_grassland_remaining_SOC_per_ha
SUBMISSION, FIRST_YEAR, LAST_YEAR = 2025, 2019, 2023


def db_value(name):
    return Emissions_Factors("ireland").get_emission_factor_in_emission_factor_data_base(name)


class TestImpliedGrasslandFactor(unittest.TestCase):
    def test_derivation_matches_database(self):
        from derive_implied_grassland_factor import derive
        got = derive(CSV, SUBMISSION, FIRST_YEAR, LAST_YEAR)
        self.assertAlmostEqual(db_value("ef_co2_implied_grassland_remaining_SOC_per_ha"), got["kgCO2_per_ha_yr"], places=6)

    def test_derivation_is_sum_kt_over_sum_area(self):
        from derive_implied_grassland_factor import derive
        d = pd.read_csv(CSV)
        w = d[(d.submission == SUBMISSION) & d.year.between(FIRST_YEAR, LAST_YEAR)]
        self.assertEqual(len(w), 5)
        by_hand = w.mineral_soil_ktCO2.sum() / w.mineral_area_kha.sum() * 1000
        self.assertAlmostEqual(derive(CSV, SUBMISSION, FIRST_YEAR, LAST_YEAR)["kgCO2_per_ha_yr"], by_hand, places=9)
        self.assertAlmostEqual(by_hand, -394.7005, places=3)  # hand check from the five yearly values

    def test_value_is_a_removal_within_the_recent_inventory_range(self):
        v = db_value("ef_co2_implied_grassland_remaining_SOC_per_ha")
        d = pd.read_csv(CSV)
        recent = d[(d.submission == SUBMISSION) & d.year.between(FIRST_YEAR, LAST_YEAR)].kgCO2_per_ha_yr
        self.assertLess(v, 0)
        self.assertTrue(recent.min() <= v <= recent.max())

    def test_provenance_record_states_value_window_and_source(self):
        text = open(PROVENANCE, encoding="utf-8").read()
        for needle in ("ef_co2_implied_grassland_remaining_SOC_per_ha", "-394.70", "2019", "2023",
                       "2025 submission", "CRF Table 4.C", "sum of kt", "ef_co2_implied_forest_to_grassland_SOC_per_ha"):
            with self.subTest(needle=needle):
                self.assertIn(needle, text)


if __name__ == "__main__":
    unittest.main()

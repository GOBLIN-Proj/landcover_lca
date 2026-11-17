"""The implied emission factors in the database are derived values: each must be reproducible
from the stored CRT extract, and documented in docs/emission_factor_provenance.md.

Run from landcover_lca/tests:  python -m unittest implied_factor_test.py
"""
import os
import sys
import unittest

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))

from landcover_lca.models import Emissions_Factors

CSV = "./data/inventory/crt2026_4c_mineral_soils.csv"
PROVENANCE = os.path.join(HERE, "..", "docs", "emission_factor_provenance.md")

# The derivation chosen for both factors: latest five years of the 2026 submission
SUBMISSION, FIRST_YEAR, LAST_YEAR = 2026, 2020, 2024
GRASS = "ef_co2_implied_grassland_remaining_SOC_per_ha"
FOREST = "ef_co2_implied_forest_to_grassland_SOC_per_ha"


def db_value(name):
    return Emissions_Factors("ireland").get_emission_factor_in_emission_factor_data_base(name)


def window(category):
    d = pd.read_csv(CSV)
    return d[d.category.str.startswith(category) & (d.submission == SUBMISSION) & d.year.between(FIRST_YEAR, LAST_YEAR)]


class TestImpliedGrasslandFactor(unittest.TestCase):
    def test_derivation_matches_database(self):
        from derive_implied_grassland_factor import derive
        got = derive(CSV, SUBMISSION, FIRST_YEAR, LAST_YEAR, "4.C.1")
        self.assertAlmostEqual(db_value(GRASS), got["kgCO2_per_ha_yr"], places=6)

    def test_derivation_is_sum_kt_over_sum_area(self):
        w = window("4.C.1")
        self.assertEqual(len(w), 5)
        by_hand = w.mineral_soil_ktCO2.sum() / w.mineral_area_kha.sum() * 1000
        self.assertAlmostEqual(db_value(GRASS), by_hand, places=6)
        self.assertAlmostEqual(by_hand, -392.7346, places=3)  # hand check: -7,593.19 kt / 19,334.16 kha

    def test_value_is_a_removal_within_the_recent_inventory_range(self):
        w = window("4.C.1").kgCO2_per_ha_yr
        self.assertLess(db_value(GRASS), 0)
        self.assertTrue(w.min() <= db_value(GRASS) <= w.max())

    def test_crt_total_agrees_with_nid_2026(self):
        # NID 2026 key category table: 4.C.1 Grassland remaining grassland, mineral soils, 2024 = -1,549.47 kt CO2
        d = pd.read_csv(CSV)
        row = d[d.category.str.startswith("4.C.1") & (d.year == 2024)].iloc[0]
        self.assertAlmostEqual(row.mineral_soil_ktCO2, -1549.47, places=1)


class TestImpliedForestToGrasslandFactor(unittest.TestCase):
    def test_derivation_matches_database(self):
        from derive_implied_grassland_factor import derive
        got = derive(CSV, SUBMISSION, FIRST_YEAR, LAST_YEAR, "4.C.2")
        self.assertAlmostEqual(db_value(FOREST), got["kgCO2_per_ha_yr"], places=6)

    def test_inventory_applies_one_constant_per_hectare_rate(self):
        # CRT 4.C.2 mineral soils: -0.896 t C/ha/yr (a loss) in every year => +3,285.34 kg CO2/ha/yr
        rates = window("4.C.2").kgCO2_per_ha_yr
        self.assertLess(rates.max() - rates.min(), 1e-6)
        self.assertAlmostEqual(db_value(FOREST), 0.896 * 1000 * 44 / 12, delta=0.1)

    def test_value_is_an_emission(self):
        self.assertGreater(db_value(FOREST), 0)


class TestForestRateAgainstNID(unittest.TestCase):
    """Is the forest to grassland rate right? Cross-checks of the CRT 2026 extract against the NID text."""

    DEFOR = "./data/inventory/crt2026_forest_conversions_mineral_soils.csv"
    # NID 2026 Table 6.19 (p.238), column "Mineral Soils Net CSC (kt C)", all deforestation destinations
    TABLE_6_19_MINERAL = {2010: -11.00, 2015: -13.22, 2020: -14.08, 2022: -13.35}

    def test_grassland_settlement_other_sum_to_nid_table_6_19(self):
        d = pd.read_csv(self.DEFOR)
        for year, nid in self.TABLE_6_19_MINERAL.items():
            with self.subTest(year=year):
                got = d[d.year == year].mineral_soil_ktC_crt_sign.sum()
                self.assertAlmostEqual(got, nid, delta=0.02)

    def test_other_land_uses_the_nid_rule_of_1_1_t_c_per_ha_per_year(self):
        # NID p.239: 20 per cent of 110 t C/ha over 20 years = 1.1 t C/ha/yr
        d = pd.read_csv(self.DEFOR)
        o = d[(d.destination == "other") & (d.year == 2024)].iloc[0]
        self.assertAlmostEqual(o.mineral_soil_ktC_crt_sign / o.area_kha, -1.1, places=3)

    def test_rate_is_about_17_per_cent_of_a_typical_forest_soil_stock(self):
        # database rate x 20 years = 17.9 t C/ha, against Tier 2 SOCref (mean 100.46) x forest FLU (mean 1.04)
        # = 104.5 t C/ha: 17%, close to the NID's 20% rule for settlement and other land
        loss_20yr = db_value(FOREST) / 1000 * 12 / 44 * 20
        self.assertAlmostEqual(loss_20yr / (100.46 * 1.04), 0.17, places=2)


class TestProvenanceRecord(unittest.TestCase):
    def test_provenance_record_states_values_window_and_source(self):
        text = open(PROVENANCE, encoding="utf-8").read()
        for needle in (GRASS, FOREST, "-392.73", "3,285.34", "2020-2024", "2026 submission", "CRT Table 4.C",
                       "sum of kt", "tools/extract_crt_table4c.py"):
            with self.subTest(needle=needle):
                self.assertIn(needle, text)


if __name__ == "__main__":
    unittest.main()

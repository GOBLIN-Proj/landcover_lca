"""FIRE-1: the forest wildfire factors are the 2020-2022 inventory implied factors.

factor (kg per ha burnt) = sum over 2020-2022 of CRT 2026 4(IV).A.1 + A.2 emissions
                           / sum over 2020-2022 of CRF 2024 Table4(V) area burnt (4.A.1 + 4.A.2)

The CRT 2026 leaves area burnt blank, so the CRF 2024 area (previous submission) is used. Fixtures and their
sources: data/inventory/ (see inventory_inputs.py). Derivation script: tools/derive_implied_forest_fire_factor.py.
The method behind the inventory values (NID 2026 s.6.3.4.4, IPCC 2006 eq 2.27): dry matter x Cf 0.45 x Gef
(CO2 1,569, CH4 4.7, N2O 0.26 g/kg dry matter).
"""
import os
import sqlite3
import unittest

import landcover_lca.models
import inventory_inputs as ii
from landcover_lca.database import get_database_path

DB = get_database_path()  # landcover_lca.database.DATABASE_FILE

NAMES = {
    "CO2": "ef_co2_implied_wildfire_forest",
    "CH4": "ef_ch4_implied_wildfire_forest",
    "N2O": "ef_n2o_implied_wildfire_forest",
}
GEF = {"CO2": 1569.0, "CH4": 4.7, "N2O": 0.26}  # g per kg dry matter
DRY_MATTER = {"4.A.1": 177713.0, "4.A.2": 103485.0}  # kg per ha (NID 2026 s.6.3.4.4)
CF = 0.45


def derived(gas):
    kg = sum((ii.crt(y, "IV.A.1", gas) + ii.crt(y, "IV.A.2", gas)) * 1e6 for y in ii.FIRE_YEARS)
    ha = sum(ii.burnt_ha(y, "forest_remaining", "land_converted_to_forest") for y in ii.FIRE_YEARS)
    return kg / ha


def database_cell(name, row):
    """A cell of emission_factors_land_use; row is 'source' or 'units'."""
    with sqlite3.connect(DB) as con:
        return con.execute(f'select [{name}] from emission_factors_land_use where ef_country = ?', (row,)).fetchone()[0]


class TestForestFireFactors(unittest.TestCase):
    def test_window_is_2020_2022(self):
        self.assertEqual(list(ii.FIRE_YEARS), [2020, 2021, 2022])

    def test_database_values_equal_the_derivation(self):
        for gas, name in NAMES.items():
            with self.subTest(gas=gas):
                self.assertAlmostEqual(ii.factor(name) / derived(gas), 1.0, delta=0.001)

    def test_gas_ratios_follow_the_ipcc_gef(self):
        co2 = ii.factor(NAMES["CO2"])
        for gas in ("CH4", "N2O"):
            with self.subTest(gas=gas):
                self.assertAlmostEqual((ii.factor(NAMES[gas]) / co2) / (GEF[gas] / GEF["CO2"]), 1.0, delta=0.01)

    def test_value_lies_between_the_category_values(self):
        for gas, name in NAMES.items():
            with self.subTest(gas=gas):
                low = DRY_MATTER["4.A.2"] * CF * GEF[gas] / 1000  # g to kg
                high = DRY_MATTER["4.A.1"] * CF * GEF[gas] / 1000
                self.assertTrue(low < ii.factor(name) < high)

    def test_source_and_units_cells(self):
        for gas, name in NAMES.items():
            with self.subTest(gas=gas):
                source = database_cell(name, "source")
                units = database_cell(name, "units")
                for text in ("CRT 2026", "4(IV)", "CRF 2024", "2020-2022"):
                    self.assertIn(text, source)
                self.assertEqual(units, f"kg {gas}/ha burnt")


if __name__ == "__main__":
    unittest.main()

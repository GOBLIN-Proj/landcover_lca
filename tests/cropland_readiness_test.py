"""CROP-1: grassland converted to cropland works end to end, in kg CO2, for the spans GOBLIN can ask for.

Run from landcover_lca/tests:  python -m unittest cropland_readiness_test.py

Contract recorded here (landcover_assignment writes it; see README "Cropland change: what the package assumes"):
  - New cropland comes from grassland only, as `Grassland_to_Cropland` (area in ha over the whole period).
  - New cropland is mineral soil, so no organic-cropland drainage term is needed (CR2).
  - SOC change uses LAC SOCref 85 t C/ha and the improved-grassland factor 1.14 for the converted grassland
    (GR1, an assumption) against 0.69 for cropland (NID 2026 Table 6.31).
Scenario: goblin_lite scenario 0, X ha moved from the afforestation allocation to cropland.
"""
import unittest

import pandas as pd

import landcover_lca.lca_emission as lca
from landcover_lca.models import (
    Land_Use_Features,
    load_land_use_data,
    load_transition_matrix,
)

TRANSITION = pd.read_csv("./goblin_lite_data/transition_matrix.csv", index_col=0)
LAND_USE = pd.read_csv("./goblin_lite_data/landuse_data_test_version.csv", index_col=0)
BASE_YEAR = 2020
SOCREF_LAC = 85.0
CROPLAND, IMPROVED = 0.69, 1.14
KG_CO2_PER_T_C = 1000 * 44 / 12


def run(x_ha, span=30):
    """Terms of total_co2_emission for X ha of grassland to cropland over `span` years."""
    lu, t = LAND_USE.copy(), TRANSITION.copy()
    scen = (lu.farm_id == 0) & (lu.year == 2050)
    lu.loc[scen, "year"] = BASE_YEAR + span
    cropland = scen & (lu.land_use == "cropland")
    forest = scen & (lu.land_use == "forest")
    lu.loc[cropland, "area_ha"] += x_ha
    lu.loc[forest, "area_ha"] -= x_ha
    t.loc[0, "Grassland_to_Cropland"] = x_ha
    t.loc[0, "Grassland_to_Forest"] -= x_ha
    tm = load_transition_matrix(t, "ireland", BASE_YEAR, BASE_YEAR + span)
    ld = load_land_use_data(lu, BASE_YEAR)
    a = (ld[0], ld[-BASE_YEAR], tm[0], "ireland")
    return {
        "soc": lca.mineral_soils_co2_from_grassland_to_cropland(*a),
        "cropland": lca.total_co2_emission_cropland(*a),
        "grassland": lca.total_co2_emission_grassland(*a),
        "wetland": lca.total_co2_emission_wetland(*a),
        "forest": lca.total_co2_emission_forest(*a),
        "total": lca.total_co2_emission(*a),
    }


def hand_soc(x_ha, span):
    """NID eq 6.4.3, kg CO2/yr: annual area x min(span, 20) x (SOC_grass - SOC_crop) / 20."""
    d_soc = SOCREF_LAC * (IMPROVED - CROPLAND)
    return x_ha / span * min(span, 20) * d_soc / 20 * KG_CO2_PER_T_C


class TestGrasslandToCropland(unittest.TestCase):
    def test_no_conversion_gives_no_cropland_co2(self):
        self.assertEqual(run(0.0)["cropland"], 0)

    def test_30_year_span_matches_hand_value_in_kg_co2(self):
        r = run(100_000.0, 30)
        self.assertAlmostEqual(r["soc"], hand_soc(100_000.0, 30), places=3)
        self.assertAlmostEqual(r["soc"], 467_500_000.0, places=3)  # 100,000 ha -> 467.5 kt CO2/yr

    def test_15_year_span_runs_and_matches_hand_value(self):
        r = run(100_000.0, 15)  # D1: this span used to return None
        self.assertAlmostEqual(r["soc"], hand_soc(100_000.0, 15), places=3)

    def test_20_year_span_is_the_whole_area_over_20_cohorts(self):
        r = run(100_000.0, 20)
        self.assertAlmostEqual(r["soc"], hand_soc(100_000.0, 20), places=3)

    def test_conversion_is_an_emission(self):
        self.assertGreater(run(1_000.0, 30)["soc"], 0)

    def test_cropland_total_is_the_soc_term(self):
        """Cropland has no other CO2 term here: new land is mineral, so no drainage (CR2)."""
        r = run(100_000.0, 30)
        self.assertAlmostEqual(r["cropland"], r["soc"], places=3)

    def test_other_land_uses_do_not_move_except_forest(self):
        base, r = run(0.0), run(100_000.0)
        self.assertEqual(r["grassland"], base["grassland"])
        self.assertEqual(r["wetland"], base["wetland"])
        self.assertLess(r["forest"], base["forest"])  # less forest area

    def test_national_total_moves_by_the_cropland_term_and_the_forest_term(self):
        base, r = run(0.0), run(100_000.0)
        self.assertAlmostEqual(
            r["total"] - base["total"],
            (r["cropland"] - base["cropland"]) + (r["forest"] - base["forest"]),
            places=3,
        )

    def test_result_is_linear_in_converted_area(self):
        self.assertAlmostEqual(
            run(200_000.0, 30)["soc"], 2 * run(100_000.0, 30)["soc"], places=3
        )


class TestImprovedGrasslandAssumption(unittest.TestCase):
    """GR1: all converted grassland is taken as improved (1.14). Records the sensitivity."""

    def test_database_factors(self):
        feats = Land_Use_Features("ireland")
        get = feats.get_landuse_features_in_land_use_features_data_base
        self.assertEqual(get("Adjustement_factor", "grassland"), IMPROVED)
        self.assertEqual(get("Adjustement_factor", "cropland"), CROPLAND)

    def test_sensitivity_to_unimproved_share(self):
        """Unimproved grassland has factor 1.0 (NID Table 6.31). Share u unimproved scales the
        emission by 1 - u x (1.14 - 1.0) / (1.14 - 0.69)."""
        drop_per_10_percent = 0.1 * (IMPROVED - 1.0) / (IMPROVED - CROPLAND)
        self.assertAlmostEqual(drop_per_10_percent, 0.0311, places=4)  # 3.1% per 10%
        self.assertAlmostEqual((IMPROVED - 1.0) / (IMPROVED - CROPLAND), 0.311, places=3)


if __name__ == "__main__":
    unittest.main()

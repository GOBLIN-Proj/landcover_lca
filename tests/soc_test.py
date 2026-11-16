"""D1: mineral-soil SOC change must return a number for every span (S1).

Run from landcover_lca/tests:  python -m unittest soc_test.py

Expected values are hand calculations, NID 2026 eq 6.4.3 (T = 20 yr):
    rate in target year = A_total / span * min(span, 20) * (SOC_past - SOC_current) / 20
with SOC = SOCref x adjustment factor. SOCref here is the package's current weighting
(0.01*95 + 0.71*85 + 0.10*115 + 0.01*71 = 73.51; D4 may change it).
Units are t C per year (D2 converts to kg CO2 later).
"""
import unittest

import pandas as pd

from landcover_lca.models import load_transition_matrix, load_land_use_data
import landcover_lca.lca_emission as lca

SOC_REF = 73.51
AREA = 1000.0
FACTORS = {"cropland": 0.69, "grassland": 1.14, "forest": 1.04}

TRANSITION = pd.read_csv("./goblin_lite_data/transition_matrix.csv", index_col=0)
LAND_USE = pd.read_csv("./goblin_lite_data/landuse_data_test_version.csv", index_col=0)


def expected(past, current, span, area=AREA):
    d_soc = SOC_REF * (FACTORS[past] - FACTORS[current])
    return area / span * min(span, 20) * d_soc / 20


def old_loop(annual_area, d_soc, span):
    """The pre-fix logic, kept here as the reference for spans over 20 years."""
    soc = 0
    for year in range(span):
        if year < 20:
            soc += annual_area * d_soc / 20
        else:
            return soc
    return None


def run(column, func, span, area=AREA):
    target = 2020 + span
    lu = LAND_USE.copy()
    lu.loc[lu.year == 2050, "year"] = target
    t = TRANSITION.copy()
    t.loc[0, column] = area
    tm = load_transition_matrix(t, "ireland", 2020, target)
    ld = load_land_use_data(lu, 2020)
    return func(ld[0], ld[-2020], tm[0], "ireland")


class TestSocSpan(unittest.TestCase):
    def test_grassland_to_cropland_every_span(self):
        for span in (1, 5, 10, 15, 19, 20, 21, 25, 30, 60):
            with self.subTest(span=span):
                got = run("Grassland_to_Cropland", lca.mineral_soils_co2_from_grassland_to_cropland, span)
                self.assertIsNotNone(got)
                self.assertAlmostEqual(got, expected("grassland", "cropland", span), places=6)

    def test_forest_to_grassland_every_span(self):
        for span in (5, 15, 20, 21, 30):
            with self.subTest(span=span):
                got = run("Forest_to_Grassland", lca.mineral_soils_co2_from_forest_to_grassland, span)
                self.assertIsNotNone(got)
                self.assertAlmostEqual(got, expected("forest", "grassland", span), places=6)

    def test_hand_values(self):
        # 1,000 ha grassland -> cropland: 73.51 x 0.45 = 33.0795 t C/ha
        self.assertAlmostEqual(
            run("Grassland_to_Cropland", lca.mineral_soils_co2_from_grassland_to_cropland, 15), 1653.975, places=3)
        self.assertAlmostEqual(
            run("Grassland_to_Cropland", lca.mineral_soils_co2_from_grassland_to_cropland, 30), 1102.65, places=2)

    def test_constant_for_spans_up_to_20(self):
        a = run("Grassland_to_Cropland", lca.mineral_soils_co2_from_grassland_to_cropland, 5)
        b = run("Grassland_to_Cropland", lca.mineral_soils_co2_from_grassland_to_cropland, 20)
        self.assertAlmostEqual(a, b, places=9)

    def test_matches_old_loop_over_20_years(self):
        d_soc = SOC_REF * (FACTORS["grassland"] - FACTORS["cropland"])
        for span in range(21, 61):
            with self.subTest(span=span):
                got = run("Grassland_to_Cropland", lca.mineral_soils_co2_from_grassland_to_cropland, span)
                self.assertAlmostEqual(got, old_loop(AREA / span, d_soc, span), places=6)

    def test_zero_area_returns_zero(self):
        got = run("Grassland_to_Cropland", lca.mineral_soils_co2_from_grassland_to_cropland, 15, area=0.0)
        self.assertEqual(got, 0)

    def test_zero_span_returns_zero(self):
        # baseline call: same dataset as current and past -> span 0
        tm = load_transition_matrix(TRANSITION, "ireland", 2020, 2050)
        ld = load_land_use_data(LAND_USE, 2020)
        got = lca.mineral_soils_co2_from_grassland_to_cropland(ld[-2020], ld[-2020], tm[-2020], "ireland")
        self.assertEqual(got, 0)

    def test_negative_span_raises(self):
        lu = LAND_USE.copy()
        lu.loc[lu.year == 2050, "year"] = 2010
        t = TRANSITION.copy()
        t.loc[0, "Grassland_to_Cropland"] = AREA
        tm = load_transition_matrix(t, "ireland", 2020, 2050)
        ld = load_land_use_data(lu, 2020)
        with self.assertRaises(ValueError):
            lca.mineral_soils_co2_from_grassland_to_cropland(ld[0], ld[-2020], tm[0], "ireland")


if __name__ == "__main__":
    unittest.main()

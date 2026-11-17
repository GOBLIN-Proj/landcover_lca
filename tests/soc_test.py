"""D1: mineral-soil SOC change must return a number for every span (S1).

Run from landcover_lca/tests:  python -m unittest soc_test.py

Expected values are hand calculations, NID 2026 eq 6.4.3 (T = 20 yr):
    rate in target year = A_total / span * min(span, 20) * (SOC_past - SOC_current) / 20
with SOC = SOCref x adjustment factor. SOCref: any transition involving cropland uses
LAC = 85 t C/ha (NID s.6.4.6, Table 6.28; D4a). Other transitions use the package's
weighted mean (0.01*95 + 0.71*85 + 0.10*115 + 0.01*71 = 73.51; D4b may change it).
D1 tests use the SOC class (t C per year). Units: the SOC class returns t C per year; the lca_emission CO2 functions return kg CO2 per year (D2).
"""
import unittest

import pandas as pd

from landcover_lca.models import load_transition_matrix, load_land_use_data
import landcover_lca.lca_emission as lca

SOC_REF = 73.51  # weighted mean, transitions without cropland
SOC_REF_CROPLAND = 85.0  # LAC, transitions involving cropland (D4a)
AREA = 1000.0
FACTORS = {"cropland": 0.69, "grassland": 1.14, "forest": 1.04}

TRANSITION = pd.read_csv("./goblin_lite_data/transition_matrix.csv", index_col=0)
LAND_USE = pd.read_csv("./goblin_lite_data/landuse_data_test_version.csv", index_col=0)


def expected(past, current, span, area=AREA):
    ref = SOC_REF_CROPLAND if "cropland" in (past, current) else SOC_REF
    d_soc = ref * (FACTORS[past] - FACTORS[current])
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


def run_tc(column, func, span, area=AREA):
    """SOC class result for the same transition as `func`, in t C per year (the D1 unit)."""
    from landcover_lca.land_classes.soc import SOC
    _, past, current = CO2_CALLERS[func.__name__]
    target = 2020 + span
    lu = LAND_USE.copy()
    lu.loc[lu.year == 2050, "year"] = target
    t = TRANSITION.copy()
    t.loc[0, column] = area
    tm = load_transition_matrix(t, "ireland", 2020, target)
    ld = load_land_use_data(lu, 2020)
    return SOC("ireland", ld[0], ld[-2020], tm[0], current, past).compute_emissions_from_mineral_soils_in_land_use_change()


class TestSocSpan(unittest.TestCase):
    def test_grassland_to_cropland_every_span(self):
        for span in (1, 5, 10, 15, 19, 20, 21, 25, 30, 60):
            with self.subTest(span=span):
                got = run_tc("Grassland_to_Cropland", lca.mineral_soils_co2_from_grassland_to_cropland, span)
                self.assertIsNotNone(got)
                self.assertAlmostEqual(got, expected("grassland", "cropland", span), places=6)

    def test_forest_to_grassland_every_span(self):
        for span in (5, 15, 20, 21, 30):
            with self.subTest(span=span):
                got = run_tc("Forest_to_Grassland", lca.mineral_soils_co2_from_forest_to_grassland, span)
                self.assertIsNotNone(got)
                self.assertAlmostEqual(got, expected("forest", "grassland", span), places=6)

    def test_hand_values(self):
        # 1,000 ha grassland -> cropland: 85 x 0.45 = 38.25 t C/ha
        self.assertAlmostEqual(
            run_tc("Grassland_to_Cropland", lca.mineral_soils_co2_from_grassland_to_cropland, 15), 1912.5, places=3)
        self.assertAlmostEqual(
            run_tc("Grassland_to_Cropland", lca.mineral_soils_co2_from_grassland_to_cropland, 30), 1275.0, places=2)

    def test_constant_for_spans_up_to_20(self):
        a = run_tc("Grassland_to_Cropland", lca.mineral_soils_co2_from_grassland_to_cropland, 5)
        b = run_tc("Grassland_to_Cropland", lca.mineral_soils_co2_from_grassland_to_cropland, 20)
        self.assertAlmostEqual(a, b, places=9)

    def test_matches_old_loop_over_20_years(self):
        d_soc = SOC_REF_CROPLAND * (FACTORS["grassland"] - FACTORS["cropland"])
        for span in range(21, 61):
            with self.subTest(span=span):
                got = run_tc("Grassland_to_Cropland", lca.mineral_soils_co2_from_grassland_to_cropland, span)
                self.assertAlmostEqual(got, old_loop(AREA / span, d_soc, span), places=6)

    def test_zero_area_returns_zero(self):
        got = run_tc("Grassland_to_Cropland", lca.mineral_soils_co2_from_grassland_to_cropland, 15, area=0.0)
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


# ---------------------------------------------------------------- D2: units
T_C_TO_KG_CO2 = 1000.0 * 44.0 / 12.0  # t C -> kg CO2

CO2_CALLERS = {
    # function: (column in transition matrix, past, current)
    "mineral_soils_co2_from_grassland_to_cropland": ("Grassland_to_Cropland", "grassland", "cropland"),
    "mineral_soils_co2_from_forest_to_grassland": ("Forest_to_Grassland", "forest", "grassland"),
    "mineral_soils_co2_from_cropland_to_grassland": ("Cropland_to_Grassland", "cropland", "grassland"),
    "mineral_soils_co2_from_forest_to_cropland": ("Forest_to_Cropland", "forest", "cropland"),
    "mineral_soils_co2_from_cropland_to_forest": ("Cropland_to_Forest", "cropland", "forest"),
    "mineral_soils_co2_from_grassland_to_forest": ("Grassland_to_Forest", "grassland", "forest"),
}


class TestCroplandUsesLAC(unittest.TestCase):
    """D4a: every transition involving cropland uses SOCref LAC = 85; others keep 73.51."""

    def soc(self, past, current):
        from landcover_lca.land_classes.soc import SOC
        tm = load_transition_matrix(TRANSITION, "ireland", 2020, 2050)
        ld = load_land_use_data(LAND_USE, 2020)
        return SOC("ireland", ld[0], ld[-2020], tm[0], current, past)

    def test_socref_by_transition(self):
        for past, cur, ref in (
            ("grassland", "cropland", 85.0), ("forest", "cropland", 85.0),
            ("cropland", "grassland", 85.0), ("cropland", "forest", 85.0),
            ("forest", "grassland", 73.51), ("grassland", "forest", 73.51),
        ):
            with self.subTest(transition=f"{past}->{cur}"):
                self.assertAlmostEqual(self.soc(past, cur).compute_SOC_ref_for_land_use(), ref, places=6)

    def test_hand_values_t_c(self):
        # 15 yr, 1,000 ha: forest -> cropland 85 x (1.04-0.69) x 1000 / 20 = 1,487.5 t C/yr
        self.assertAlmostEqual(
            run_tc("Forest_to_Cropland", lca.mineral_soils_co2_from_forest_to_cropland, 15), 1487.5, places=3)
        # cropland -> grassland: 85 x (0.69-1.14) x 1000 / 20 = -1,912.5 (a removal)
        self.assertAlmostEqual(
            run_tc("Cropland_to_Grassland", lca.mineral_soils_co2_from_cropland_to_grassland, 15), -1912.5, places=3)

    def test_forest_to_grassland_still_weighted_mean(self):
        # 73.51 x (1.04-1.14) x 1000 / 20 = -367.55
        self.assertAlmostEqual(
            run_tc("Forest_to_Grassland", lca.mineral_soils_co2_from_forest_to_grassland, 15), -367.55, places=3)


class TestSocUnitsKgCO2(unittest.TestCase):
    """The lca_emission CO2 functions return kg CO2 per year (positive = emission)."""

    def test_hand_values_kg_co2(self):
        # 1,000 ha grassland -> cropland: 1,912.5 t C/yr (<=20 yr) and 1,275 t C/yr (30 yr)
        g15 = run("Grassland_to_Cropland", lca.mineral_soils_co2_from_grassland_to_cropland, 15)
        g30 = run("Grassland_to_Cropland", lca.mineral_soils_co2_from_grassland_to_cropland, 30)
        self.assertAlmostEqual(g15, 7012500.0, places=3)
        self.assertAlmostEqual(g30, 4675000.0, places=3)

    def test_every_caller_is_t_c_times_44_12_times_1000(self):
        for name, (col, past, cur) in CO2_CALLERS.items():
            for span in (10, 30):
                with self.subTest(function=name, span=span):
                    got = run(col, getattr(lca, name), span)
                    self.assertAlmostEqual(got, expected(past, cur, span) * T_C_TO_KG_CO2, places=3)

    def test_sign_positive_emission_negative_removal(self):
        self.assertGreater(run("Grassland_to_Cropland", lca.mineral_soils_co2_from_grassland_to_cropland, 30), 0)
        self.assertLess(run("Forest_to_Grassland", lca.mineral_soils_co2_from_forest_to_grassland, 30), 0)

    def test_n2o_caller_unchanged_by_d2(self):
        # still t C x 1/15 until D5
        got = run("Forest_to_Grassland", lca.mineral_soils_n2o_from_forest_to_grassland, 30)
        self.assertAlmostEqual(got, expected("forest", "grassland", 30) / 15.0, places=6)

    def test_soc_class_still_returns_t_c(self):
        from landcover_lca.land_classes.soc import SOC
        tm = load_transition_matrix(TRANSITION.assign(**{"Grassland_to_Cropland": AREA}), "ireland", 2020, 2050)
        ld = load_land_use_data(LAND_USE, 2020)
        soc = SOC("ireland", ld[0], ld[-2020], tm[0], "cropland", "grassland")
        self.assertAlmostEqual(soc.compute_emissions_from_mineral_soils_in_land_use_change(), 1275.0, places=2)

    def test_goblin_lite_scaling_example(self):
        # goblin_lite multiplies by kg_to_kt = 1e-6 and nothing else
        got = run("Grassland_to_Cropland", lca.mineral_soils_co2_from_grassland_to_cropland, 30)
        self.assertAlmostEqual(got * 1e-6, 4.675, places=5)  # kt CO2 per year

    def test_national_total_unchanged(self):
        # Goblin_lite national case. Values moved by D7 only (grassland remaining factor -371.985 -> -394.70);
        # before D7: 3785608957.9, 4637503163.5, 4640527270.9. D1-D6 change nothing here (zero conversion areas).
        t = TRANSITION
        tm = load_transition_matrix(t, "ireland", 2020, 2050)
        ld = load_land_use_data(LAND_USE, 2020)
        self.assertAlmostEqual(lca.total_co2_emission(ld[-2020], ld[-2020], tm[-2020], "ireland"), 3703931207.8, delta=0.1)
        self.assertAlmostEqual(lca.total_co2_emission(ld[0], ld[-2020], tm[0], "ireland"), 4620246661.6, delta=0.1)
        self.assertAlmostEqual(lca.total_co2_emission(ld[1], ld[-2020], tm[1], "ireland"), 4623455773.3, delta=0.1)


if __name__ == "__main__":
    unittest.main()

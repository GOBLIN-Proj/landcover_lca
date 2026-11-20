"""D5: N2O from the loss of soil carbon (NID eq 11.8, 11.10): forest converted to grassland.

Run from landcover_lca/tests:  python -m unittest soc_n2o_test.py

The chain (NID 2026 s.6.3.6.2 p.239; CRT Table 4(III) row 4(III).C.2.a):
    N mineralised   = soil C lost / 15                                  (C:N ratio 15)
    direct N2O-N    = N mineralised x EF1 (0.006)
    indirect N2O-N  = N mineralised x FracLEACH (0.1) x EF5 (0.011)
    N2O             = N2O-N x 44/28
Unit contract: kg N2O per year (goblin_lite multiplies by 1e-6, then applies the GWP).
"""
import unittest

import pandas as pd

import landcover_lca.lca_emission as lca
from landcover_lca.models import load_transition_matrix, load_land_use_data

TRANSITION = pd.read_csv("./goblin_lite_data/transition_matrix.csv", index_col=0)
LAND_USE = pd.read_csv("./goblin_lite_data/landuse_data_test_version.csv", index_col=0)
N2O = pd.read_csv("./data/inventory/crt2026_4iii_forest_to_grassland_n2o.csv")
SOIL = pd.read_csv("./data/inventory/crt2026_forest_conversions_mineral_soils.csv")

FACTOR = (0.006 + 0.1 * 0.011) * 44 / 28     # kg N2O per kg N mineralised (direct + indirect)


def run_n2o(span, area=1000.0):
    target = 2020 + span
    lu = LAND_USE.copy()
    lu.loc[lu.year == 2050, "year"] = target
    t = TRANSITION.copy()
    t.loc[0, "Forest_to_Grassland"] = area
    tm = load_transition_matrix(t, "ireland", 2020, target)
    ld = load_land_use_data(lu, 2020)
    return lca.mineral_soils_n2o_from_forest_to_grassland(ld[0], ld[-2020], tm[0], "ireland")


# kg N2O, goblin_lite national case (baseline 2020, scenarios 0 and 1 in 2050), measured before D5
# goblin_lite national N2O (kg). D5 changes nothing here. FIRE-1 adds 177.6534 ha x (17.3047 - 10.4615) kg N2O/ha
# = 1,215.719 kg; before FIRE-1: 616310.977184324, 616059.4020200202, 616058.6795489962.
NATIONAL_N2O = [617526.696301, 617275.121136, 617274.398665]


class TestInventoryChain(unittest.TestCase):
    """The package's helper reproduces the inventory's own N2O for forest land converted to grassland."""

    def test_nitrogen_mineralised_is_soil_carbon_loss_over_15(self):
        for year in (1995, 2005, 2015, 2022, 2024):
            with self.subTest(year=year):
                loss_kt_c = -SOIL[(SOIL.destination == "grassland") & (SOIL.year == year)].mineral_soil_ktC_crt_sign.iloc[0]
                n = N2O[N2O.year == year].n_mineralised_t_n.iloc[0]
                self.assertAlmostEqual(loss_kt_c * 1000 / 15, n, delta=0.001 * n)

    def test_helper_reproduces_crt_total_n2o_every_year(self):
        d = N2O[N2O.total_kt_n2o >= 0.002]            # years where the CRT value has 3+ significant digits
        self.assertGreater(len(d), 10)
        for r in d.itertuples():
            with self.subTest(year=r.year):
                got_kg = lca.n2o_from_soil_carbon_loss(r.n_mineralised_t_n * 15)   # t C lost
                self.assertAlmostEqual(got_kg, r.total_kt_n2o * 1e6, delta=0.01 * r.total_kt_n2o * 1e6)

    def test_direct_and_indirect_parts_2022(self):
        r = N2O[N2O.year == 2022].iloc[0]
        self.assertAlmostEqual(r.n_mineralised_t_n * 1000 * 0.006 * 44 / 28, r.direct_kt_n2o * 1e6, delta=0.01 * r.direct_kt_n2o * 1e6)
        self.assertAlmostEqual(r.n_mineralised_t_n * 1000 * 0.1 * 0.011 * 44 / 28, r.indirect_kt_n2o * 1e6, delta=0.01 * r.indirect_kt_n2o * 1e6)

    def test_2022_value_by_hand(self):
        # 7,901.8 t C lost -> 526.79 t N -> 5,877 kg N2O (CRT: 0.00588 kt)
        self.assertAlmostEqual(lca.n2o_from_soil_carbon_loss(7901.8), 5877.0, delta=2.0)


class TestPackageCaller(unittest.TestCase):
    def test_caller_is_kg_n2o_from_soc_t_c(self):
        # 1,000 ha forest -> grassland, 30 years: SOC = 73.51 x (1.04 - 1.14) x 1000 / 30 x 20 / 20 = -245.03 t C/yr
        soc_t_c = 73.51 * (1.04 - 1.14) * 1000 / 30
        self.assertAlmostEqual(run_n2o(30), soc_t_c * 1000 / 15 * FACTOR, places=3)    # -182.25 kg N2O/yr
        self.assertAlmostEqual(run_n2o(30), -182.25, places=1)

    def test_factor_is_eleven_times_the_old_value(self):
        # old: t C / 15, returned as if it were kg N2O
        self.assertAlmostEqual(FACTOR * 1000, 11.157, places=2)

    def test_sign_follows_soil_carbon(self):
        # Tier 1 gives a gain of soil carbon for forest -> grassland (D4b gap), so the package value is negative
        self.assertLess(run_n2o(30), 0)

    def test_zero_area_returns_zero(self):
        self.assertEqual(run_n2o(15, area=0.0), 0)

    def test_total_n2o_grassland_includes_it(self):
        tm = load_transition_matrix(TRANSITION.assign(Forest_to_Grassland=1000.0), "ireland", 2020, 2050)
        ld = load_land_use_data(LAND_USE, 2020)
        with_it = lca.total_n2o_emission_grassland(ld[0], ld[-2020], tm[0], "ireland")
        tm0 = load_transition_matrix(TRANSITION, "ireland", 2020, 2050)
        without = lca.total_n2o_emission_grassland(ld[0], ld[-2020], tm0[0], "ireland")
        self.assertAlmostEqual(with_it - without, run_n2o(30), places=3)

    def test_national_n2o_total_unchanged(self):
        # zero conversion areas in the goblin_lite national case: D5 changes nothing there
        tm = load_transition_matrix(TRANSITION, "ireland", 2020, 2050)
        ld = load_land_use_data(LAND_USE, 2020)
        got = [lca.total_n2o_emission(ld[i], ld[-2020], tm[i], "ireland") for i in (-2020, 0, 1)]
        for g, want in zip(got, NATIONAL_N2O):
            self.assertAlmostEqual(g, want, delta=1e-3)



if __name__ == "__main__":
    unittest.main()

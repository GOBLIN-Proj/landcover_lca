"""Layer B: SOC constants and per-hectare results against the Ireland NID 2026.

Run from landcover_lca/tests:  python -m unittest soc_inventory_test.py
Fixture: data/inventory/nid2026_soc_reference.csv (table and page in `source`).

The NID reports no land converted to cropland (CRT 4.B.2 is NO), so there is no inventory
total for grassland to cropland. The inventory's cropland SOC numbers come from the rotation
approach, Table 6.32: a parcel under grass (temporary grassland, AF 0.82) converted to crop
(AF 0.69) falls from 69.7 to 58.7 t C/ha over 20 years. Same equation (6.4.3), same
adjustment factors, so it is a real inventory value to match.
"""
import unittest

import pandas as pd

import landcover_lca.lca_emission as lca
from landcover_lca.resource_manager.data_loader import Loader
from landcover_lca.models import Land_Use_Features

from landcover_lca.models import load_transition_matrix, load_land_use_data
from landcover_lca.land_classes.soc import SOC

REF = pd.read_csv("./data/inventory/nid2026_soc_reference.csv").set_index("quantity")["value"]
TRANSITION = pd.read_csv("./goblin_lite_data/transition_matrix.csv", index_col=0)
LAND_USE = pd.read_csv("./goblin_lite_data/landuse_data_test_version.csv", index_col=0)


CRF = pd.read_csv("./data/inventory/crf_4c1_grassland_remaining_mineral.csv")


def crf(submission, year, column):
    row = CRF[(CRF.submission == submission) & (CRF.year == year)]
    return float(row[column].iloc[0])


def soc_object(current="cropland", past="grassland"):
    tm = load_transition_matrix(TRANSITION, "ireland", 2020, 2050)
    ld = load_land_use_data(LAND_USE, 2020)
    return SOC("ireland", ld[0], ld[-2020], tm[0], current, past)


class TestInventoryConstants(unittest.TestCase):
    """The NID constants themselves reproduce the NID's own Table 6.32 (checks our reading)."""

    def test_table_6_32_endpoints_from_6_28_and_6_31(self):
        crop = REF["SOCref LAC"] * REF["AF cropland"]
        temp_grass = REF["SOCref LAC"] * REF["AF temporary grassland"]
        self.assertAlmostEqual(crop, 58.65, places=2)
        self.assertAlmostEqual(crop, REF["SOC under crops at year 0 (crops under grass table)"], delta=0.06)
        self.assertAlmostEqual(temp_grass, REF["SOC under grass at year 0 (grass under crop table)"], delta=0.01)

    def test_table_6_32_20_year_loss_and_annual_rate(self):
        d_soc = REF["SOC under grass at year 0 (grass under crop table)"] - REF["SOC grass-under-crop after 20 years"]
        self.assertAlmostEqual(d_soc, 11.0, places=6)
        self.assertAlmostEqual(d_soc / 20, 0.55, places=6)  # t C/ha/yr, eq 6.4.3 with T = 20
        # linear in the table: halfway after 10 years
        self.assertAlmostEqual(REF["SOC under grass at year 0 (grass under crop table)"] - REF["SOC grass-under-crop after 10 years"], 5.5, places=6)

    def test_table_6_28_proportions(self):
        mineral = sum(REF[f"Proportion {k}"] for k in ("HAC", "LAC", "Peaty/Humic", "Sandy"))
        self.assertAlmostEqual(mineral, 0.83, places=6)
        self.assertAlmostEqual(mineral + REF["Proportion wetland soils (organic)"], 1.0, places=6)


class TestPackageAgainstInventory(unittest.TestCase):
    def test_package_soc_ref_is_the_unnormalised_weighted_mean(self):
        # transitions without cropland: 73.51, not renormalised (88.57). D4b may change it.
        self.assertAlmostEqual(soc_object("grassland", "forest").compute_SOC_ref_for_land_use(), 73.51, places=6)

    def test_cropland_transitions_use_lac_socref(self):
        # NID s.6.4.6, Table 6.28: LAC 85 (D4a)
        for current, past in (("cropland", "grassland"), ("cropland", "forest"), ("grassland", "cropland")):
            with self.subTest(past=past, current=current):
                self.assertAlmostEqual(soc_object(current, past).compute_SOC_ref_for_land_use(), REF["SOCref LAC"], places=6)

    def test_package_adjustment_factors_match_table_6_31(self):
        s = soc_object()
        ref = s.compute_SOC_ref_for_land_use()
        self.assertAlmostEqual(s.compute_emission_factor_from_mineral_soils("cropland") / ref, REF["AF cropland"], places=9)
        self.assertAlmostEqual(s.compute_emission_factor_from_mineral_soils("grassland") / ref, REF["AF improved grassland"], places=9)
        self.assertAlmostEqual(s.compute_emission_factor_from_mineral_soils("Temporary grassland") / ref, REF["AF temporary grassland"], places=9)

    def test_temporary_grass_to_crop_loss_matches_table_6_32(self):
        """Table 6.32: 11.0 t C/ha (SOCref 85, LAC). D4a: cropland transitions use LAC 85."""
        s = soc_object()
        d_soc = (s.compute_emission_factor_from_mineral_soils("Temporary grassland")
                 - s.compute_emission_factor_from_mineral_soils("cropland"))
        self.assertAlmostEqual(d_soc, 11.0, delta=0.11)  # 1% tolerance


class TestDatabaseAgainstInventory(unittest.TestCase):
    """Database values against NID 2026 Tables 6.28 and 6.31."""

    def test_soil_class_table_matches_table_6_28(self):
        db = Loader("ireland").ipcc_soc_factors().set_index("IPCCSoilClass")
        for db_name, key in (("HAC", "HAC"), ("LAC", "LAC"), ("Peaty/ Humic", "Peaty/Humic"), ("Sandy Soil", "Sandy")):
            with self.subTest(soil=key):
                self.assertAlmostEqual(float(db.loc[db_name, "SOCref"]), REF[f"SOCref {key}"], places=6)
                self.assertAlmostEqual(float(db.loc[db_name, "Proportion"]), REF[f"Proportion {key}"], places=6)

    def test_adjustment_factors_match_table_6_31(self):
        f = Land_Use_Features("ireland").get_landuse_features_in_land_use_features_data_base
        self.assertAlmostEqual(f("Adjustement_factor", "cropland"), REF["AF cropland"])
        self.assertAlmostEqual(f("Adjustement_factor", "grassland"), REF["AF improved grassland"])
        self.assertAlmostEqual(f("Adjustement_factor", "Temporary grassland"), REF["AF temporary grassland"])
        self.assertAlmostEqual(f("Adjustement_factor", "Rough grazing"), 1.0)

    @unittest.expectedFailure
    def test_unmanaged_grassland_factor_matches_unimproved(self):
        """DB 'Grassland (unmanaged)' is 0.95 (FMG 0.95); NID Table 6.31 unimproved is 1.0. Name mapping to confirm."""
        f = Land_Use_Features("ireland").get_landuse_features_in_land_use_features_data_base
        self.assertAlmostEqual(f("Adjustement_factor", "Grassland (unmanaged)"), REF["AF unimproved grassland"])

    def test_all_grassland_conversions_use_the_improved_factor(self):
        """Documents the assumption: every grassland conversion uses 1.14 (improved), no split."""
        s = soc_object()
        ref = s.compute_SOC_ref_for_land_use()
        self.assertAlmostEqual(s.compute_emission_factor_from_mineral_soils("grassland"), ref * REF["AF improved grassland"], places=9)


class TestGrasslandRemainingAgainstInventory(unittest.TestCase):
    """The implied factor (-394.70 kg CO2/ha/yr, CRF 4.C.1 mineral soils, 2025 submission, 2019-2023,
    sum kt / sum area; docs/emission_factor_provenance.md) and the baseline total against the CRF."""

    EF = -394.70054675481975

    def test_fixture_agrees_with_nid_table_1(self):
        # NID 2026 summary table, 4.C.1 Grassland remaining grassland mineral soils, 1990: +107.27 kt CO2
        self.assertAlmostEqual(crf(2024, 1990, "mineral_soil_ktCO2"), 107.27, places=2)

    def test_factor_is_within_the_recent_inventory_range(self):
        w = CRF[(CRF.submission == 2025) & CRF.year.between(2019, 2023)].kgCO2_per_ha_yr
        self.assertGreaterEqual(self.EF, w.min())
        self.assertLessEqual(self.EF, w.max())

    def test_factor_reproduces_2020_total_when_the_area_is_the_inventory_area(self):
        # inventory mineral area 3,880.7 kha x factor = -1,531.7 kt against -1,495.8 kt (2025 submission, 2020): 2.4%
        inv_area = crf(2025, 2020, "mineral_area_kha")
        self.assertAlmostEqual(self.EF * inv_area / 1000, crf(2025, 2020, "mineral_soil_ktCO2"),
                               delta=0.03 * 1495.8)

    def _baseline_kt(self):
        tm = load_transition_matrix(TRANSITION, "ireland", 2020, 2050)
        ld = load_land_use_data(LAND_USE, 2020)
        return lca.mineral_soils_co2_grassland_remaining_grassland(ld[-2020], ld[-2020], tm[-2020], "ireland") * 1e-6

    @unittest.expectedFailure
    def test_baseline_2020_total_vs_2025_submission(self):
        """2025 submission 2020: -1,495.8 kt. Package: -1,419.2 kt (-5.1%). The factor is right; the package
        mineral grassland area is 3,595.7 kha against the inventory 3,880.7 kha (-7.3%): landcover_assignment (LA2)."""
        self.assertAlmostEqual(self._baseline_kt(), crf(2025, 2020, "mineral_soil_ktCO2"), delta=0.03 * 1495.8)

    @unittest.expectedFailure
    def test_factor_follows_the_inventory_time_series(self):
        """A constant cannot follow the series: 1990 is +26.6 kg/ha, 2023 is -397.9 (NID Tables 1.9, 1.11). By design: the factor is a recent-years average."""
        for year in (1990, 2000, 2010):
            self.assertAlmostEqual(self.EF, crf(2025, year, "kgCO2_per_ha_yr"), delta=0.25 * abs(self.EF))


    @unittest.expectedFailure
    def test_forest_to_grassland_matches_nid_tier2_average(self):
        """D4b gap, documented not fixed. NID s.6.3.6.2 uses Tier 2: SOCref mean 100.46 (Table 6.20)
        and FLU forest 1.04, improved grassland 1.05 (Table 6.21 average): 100.46 x (1.04 - 1.05) =
        -1.0 t C/ha. The package uses 73.51 x (1.04 - 1.14) = -7.35. GOBLIN never reaches this path."""
        s = soc_object("forest", "grassland")
        d_soc = (s.compute_emission_factor_from_mineral_soils("forest")
                 - s.compute_emission_factor_from_mineral_soils("grassland"))
        self.assertAlmostEqual(d_soc, 100.46 * (1.04 - 1.05), delta=0.5)


if __name__ == "__main__":
    unittest.main()

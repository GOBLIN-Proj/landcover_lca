"""UNITS: the database stores every factor as published; resource_manager/units.py converts on read.

- The database (binary in git) equals src/landcover_lca/database/emission_factors_land_use.csv (readable, diffable):
  value, unit and source of every column.
- Every unit is one that units.py knows how to convert.
- Regression: what the calculations receive is unchanged from before (pinned below), except the changes listed in
  CHANGED, each with its reason. Both code trees (main and geo_goblin) read the same converted values.
"""
import csv
import math
import os
import sqlite3
import unittest

import landcover_lca.models as models
import landcover_lca.geo_goblin.geo_models as geo_models
from landcover_lca.resource_manager import units

HERE = os.path.dirname(models.__file__)
DB = os.path.join(HERE, "database", "landcover_lca_database.db")
CSV = os.path.join(HERE, "database", "emission_factors_land_use.csv")

# What Emissions_Factors returned before UNITS (kg CO2, kg CH4, kg N2O per ha; g per kg DM; fractions).
BEFORE = {
    "ef_co2_forest_drainage_on_site": 6165.6,
    "ef_co2_forest_drainage_off_site_DOC": 1137.7,
    "ef_ch4_forest_drainage_land": 2.5,
    "ef_ch4_forest_drainage_ditch": 217.0,
    "ef_n2o_forest_drainage_rich": 4.4,
    "ef_n2o_forest_drainage_poor": 1.1,
    "share_forest_drainage_rich": 0.125542835,
    "share_forest_drainage_poor": 0.874457165,
    "ef_co2_grassland_drainage_on_site_poor": 4771.0,
    "ef_co2_grassland_drainage_on_site_rich": 22387.0,
    "ef_co2_grassland_drainage_off_site": 1137.7,
    "ef_ch4_grassland_drainage_land_poor": 11.76,
    "ef_ch4_grassland_drainage_land_rich": 16.0,
    "ef_ch4_grassland_drainage_ditch": 1165.0,
    "frac_ditch": 0.05,
    "frac_ditch_poor": 0.0249,
    "frac_ditch_rich": 0.00375,
    "ef_n2o_grassland_drainage_poor": 6.757142857,
    "ef_n2o_grassland_drainage_rich": 12.8857142857143,
    "ef_co2_wetland_industrial_extraction_on_site": 6239.0,
    "ef_co2_wetland_drainage_DOC_default": 1137.7,
    "ef_ch4_wetland_drainage_land_default": 6.1,
    "ef_ch4_wetland_drainage_ditch_default": 542.0,
    "ef_n2o_wetland_drainage_default": 0.471428571,
    "ef_co2_wetland_rewet_on_site_default": 1835.0,
    "ef_co2_wetland_rewet_off_site_default": 880.8,
    "ef_co2_wetland_domestic_extraction_on_site": 5835.3,
    "ef_co2_near_natural_wetland_removal": -1211.1,
    "ef_co2_near_natural_wetland_runoff": 623.9,
    "ef_ch4_near_natural_wetland": 72.9333333333333,
    "ef_ch4_wetland_rewet_industrial": 216.0,
    "ef_ch4_wetland_rewet_domestic": 106.4,  # new in WET (CRT implied)
    "frac_horticultural_peat_exported": 0.85,  # new in P1 (NID 2026 s.6.6.3 p.279)
    "sd_forest_organo_mineral": 0.581,  # new in F6 (NID 2026 Tables 6.7, 6.15)
    "ef_co2_forest_rewetting_on_site": -843.3333333,
    "ef_co2_forest_rewetting_DOC": 880.0,
    "ef_ch4_forest_rewetting": 92.0,
    "ef_co2_forest_to_settlement_mineral_soil": 80666.66667,
    "ef_co2_forest_to_settlement_drainage": 3410.0,
    "ef_co2_forest_to_other_land": 3410.0,
    "ef_co2_grassland_rewetting_on_site_poor": 3119.5,
    "ef_co2_grassland_rewetting_on_site_rich": 1835.0,
    "ef_co2_grassland_rewetting_DOC": 880.0,
    "ef_ch4_grassland_rewetting_poor": 90.8,
    "ef_ch4_grassland_rewetting_rich": 288.0,
    "ef_wildfire_MB_time_CF_mineral_soil_grassland": 4.1,
    "ef_wildfire_MB_time_CF_drained_organic_soil_grassland": 336.0,
    "ef_wildfire_MB_time_CF_wet_organic_soil_grassland": 66.0,
    "ef_wildfire_GEF_n2o_mineral_soil_grassland": 0.21,
    "ef_wildfire_GEF_n2o_wet_in_organic_grassland": 0.21,
    "ef_wildfire_GEF_n2o_drained_in_organic_grassland": 0.21,
    "ef_wildfire_GEF_co2_mineral_soil_grassland": 1613.0,
    "ef_wildfire_GEF_co2_drained_organic_soil_grassland": 362.0,
    "ef_wildfire_GEF_co2_wet_organic_soil_grassland": 362.0,
    "ef_wildfire_GEF_ch4_mineral_soil_grassland": 2.3,
    "ef_wildfire_GEF_ch4_wet_in_organic_soil_grassland": 9.0,
    "ef_wildfire_GEF_ch4_drained_in_organic_grassland": 9.0,
    "ef_co2_deforestation_biomass": 305433.3333,
    "ef_co2_deforestation_DOM": 60133.33333,
    "ef_co2_implied_wildfire_forest": 104427.25352567247,
    "ef_ch4_implied_wildfire_forest": 312.8158646084511,
    "ef_n2o_implied_wildfire_forest": 17.304707403871166,
    "ef_wildfire_MB_time_CF_wetland": 336.0,
    "ef_co2_wetland_Gef": 342.0,
    "ef_ch4_wetland_Gef": 8.35,
    "ef_n2o_wetland_Gef": 0.21,
    "ef_wildfire_MB_time_CF_cropland": 4.0,
    "ef_co2_cropland_Gef": 0.0,
    "ef_ch4_cropland_Gef": 2.7,
    "ef_n2o_cropland_Gef": 0.07,
    "ef_co2_forest_share_harvested": 0.838,
    "ef_co2_forest_share_natural": 0.162,
    "ef_offsite_carbon_conversion_nutrient_poor": 1.6515,
    "ef_forest_Cf": 0.45,
    "ef_co2_peatland_to_wetland_biomass": -11000.0,
    "ef_co2_implied_grassland_remaining_SOC_per_ha": -392.73460806269964,
    "ef_co2_implied_forest_to_grassland_SOC_per_ha": 3285.338380912789,
}

ROUNDED_367 = (44 / 12) / 3.67  # was converted with 3.67 instead of 44/12: -0.09%
DOC = 0.21 * 1.6 * 0.9 * 44 / 12 * 1000 / 1137.7  # grassland, wetland: 0.3024 t C (as the CRT), not 0.31
CARBON_BASIS = 44 / 12  # published as g CO2-C per kg DM, read as g CO2 before

CHANGED = {  # name: (after / before, reason)
    **{n: (ROUNDED_367, "3.67 -> 44/12") for n in (
        "ef_co2_forest_drainage_on_site", "ef_co2_grassland_drainage_on_site_poor",
        "ef_co2_grassland_drainage_on_site_rich", "ef_co2_wetland_industrial_extraction_on_site",
        "ef_co2_wetland_rewet_on_site_default", "ef_co2_wetland_rewet_off_site_default",
        "ef_co2_wetland_domestic_extraction_on_site", "ef_co2_near_natural_wetland_removal",
        "ef_co2_near_natural_wetland_runoff", "ef_co2_grassland_rewetting_on_site_poor",
        "ef_co2_grassland_rewetting_on_site_rich", "ef_offsite_carbon_conversion_nutrient_poor",
        "ef_co2_forest_drainage_off_site_DOC")},  # forest DOC stays 0.31 t C: NID Tables 6.7, 6.15
    **{n: (DOC, "DOC 0.31 -> 0.3024 t C (IPCC 2013 eq 2.5, as the CRT)") for n in (
        "ef_co2_grassland_drainage_off_site", "ef_co2_wetland_drainage_DOC_default")},
    **{n: (CARBON_BASIS, "fire Gef published as g CO2-C/kg DM") for n in (
        "ef_co2_wetland_Gef", "ef_wildfire_GEF_co2_drained_organic_soil_grassland",
        "ef_wildfire_GEF_co2_wet_organic_soil_grassland")},
}


def published_csv():
    with open(CSV, newline="") as f:
        return {r["name"]: r for r in csv.DictReader(f)}


def db_rows():
    with sqlite3.connect(DB) as con:
        cur = con.execute("select * from emission_factors_land_use")
        cols = [d[0] for d in cur.description]
        return {r[0]: dict(zip(cols, r)) for r in cur.fetchall()}, cols[1:]


class TestDatabaseIsThePublishedTable(unittest.TestCase):
    def test_csv_and_database_have_the_same_columns(self):
        _, cols = db_rows()
        self.assertEqual(sorted(cols), sorted(published_csv()))
        self.assertEqual(sorted(cols), sorted(BEFORE))

    def test_database_equals_csv(self):
        rows, cols = db_rows()
        for name, r in published_csv().items():
            with self.subTest(name=name):
                self.assertEqual(float(rows["ireland"][name]), float(r["value"]))
                self.assertEqual(rows["units"][name], r["unit"])
                self.assertEqual(rows["source"][name], r["source"])

    def test_every_unit_is_known(self):
        for name, r in published_csv().items():
            with self.subTest(name=name):
                self.assertIn(r["unit"], units.UNITS)

    def test_unknown_unit_raises(self):
        with self.assertRaises(KeyError):
            units.to_model_units(1.0, "t CO2/ha", "x")


class TestConversions(unittest.TestCase):
    def test_constants(self):
        self.assertEqual(units.C_TO_CO2, 44 / 12)
        self.assertEqual(units.CH4_C_TO_CH4, 16 / 12)
        self.assertEqual(units.N2O_N_TO_N2O, 44 / 28)

    def test_examples(self):
        ef = models.Emissions_Factors("ireland")
        get = ef.get_emission_factor_in_emission_factor_data_base
        self.assertAlmostEqual(get("ef_co2_wetland_domestic_extraction_on_site"), 1.59 * 44 / 12 * 1000, places=9)
        self.assertAlmostEqual(get("ef_ch4_near_natural_wetland"), 54.7 * 16 / 12, places=9)
        self.assertAlmostEqual(get("ef_n2o_wetland_drainage_default"), 0.3 * 44 / 28, places=12)
        self.assertAlmostEqual(get("ef_co2_wetland_Gef"), 342 * 44 / 12, places=9)
        self.assertEqual(get("ef_ch4_wetland_Gef"), 8.35)

    def test_drained_doc_differs_by_land_use_as_in_the_inventory(self):
        # forest: 0.31 t C (NID Tables 6.7, 6.15: DOC / area = 0.310); grassland, wetland: 0.3024 (CRT implied 1108.8)
        ef = models.Emissions_Factors("ireland")
        self.assertEqual(ef.get_published_factor("ef_co2_forest_drainage_off_site_DOC")[0], 0.31)
        for name in ("ef_co2_grassland_drainage_off_site", "ef_co2_wetland_drainage_DOC_default"):
            self.assertAlmostEqual(ef.get_emission_factor_in_emission_factor_data_base(name), 1108.8, places=9)

    def test_published_value_is_available(self):
        ef = models.Emissions_Factors("ireland")
        self.assertEqual(ef.get_published_factor("ef_co2_wetland_domestic_extraction_on_site"),
                         (1.59, "t CO2-C/ha/yr"))


class TestRegression(unittest.TestCase):
    def test_values_unchanged_except_listed(self):
        main = models.Emissions_Factors("ireland").get_emission_factor_in_emission_factor_data_base
        for name, before in BEFORE.items():
            ratio = CHANGED.get(name, (1.0, ""))[0]
            with self.subTest(name=name):
                if before == 0:
                    self.assertEqual(main(name), 0.0)
                else:
                    self.assertTrue(math.isclose(main(name) / before, ratio, rel_tol=1e-8),
                                    f"{name}: {main(name)} vs {before} x {ratio}")

    def test_geo_reads_the_same_values(self):
        main = models.Emissions_Factors("ireland").get_emission_factor_in_emission_factor_data_base
        geo = geo_models.Emissions_Factors("ireland").get_emission_factor_in_emission_factor_data_base
        for name in BEFORE:
            with self.subTest(name=name):
                self.assertEqual(main(name), geo(name))


if __name__ == "__main__":
    unittest.main()

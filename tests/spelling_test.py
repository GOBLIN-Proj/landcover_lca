"""Names are spelt correctly: code identifiers, database tables, columns and lookup values.

Misspellings found in the 0.3.0 sweep are listed in MISSPELT; none may come back anywhere in src/ or the database.
The two public names that changed keep working for one release, with a DeprecationWarning:
- land_use_features column Adjustement_factor -> Adjustment_factor
- slam_nutrient_export_rates type continuos_fabric / discontinuos_fabric -> continuous_fabric / discontinuous_fabric
"""
import os
import re
import sqlite3
import unittest
import warnings

import landcover_lca.models as models
import landcover_lca.geo_goblin.geo_models as geo_models
from landcover_lca.database import get_database_path

SRC = os.path.dirname(models.__file__)
DB = get_database_path()  # landcover_lca.database.DATABASE_FILE

MISSPELT = ["adjustement", "continuos", "discontinuos", "creater", "industrail", "industral", "draingage", "disolved",
            "cacluates", "emissons", "offite", "paramters", "remainging", "deafult", "wilfire", "invetory"]


def database_names():
    con = sqlite3.connect(DB)
    names = []
    for (table,) in con.execute("select name from sqlite_master where type='table'"):
        names.append(table)
        names += [r[1] for r in con.execute(f"pragma table_info([{table}])")]
        for (col,) in [(r[1],) for r in con.execute(f"pragma table_info([{table}])")]:
            names += [str(v) for (v,) in con.execute(f"select distinct [{col}] from [{table}]") if isinstance(v, str)]
    return names


class TestNoMisspellings(unittest.TestCase):
    def test_source(self):
        pattern = re.compile("|".join(MISSPELT), re.IGNORECASE)
        hits = []
        for root, _, files in os.walk(SRC):
            for f in files:
                if f.endswith((".py", ".csv")):
                    path = os.path.join(root, f)
                    for n, line in enumerate(open(path, encoding="utf-8"), 1):
                        if pattern.search(line) and "DEPRECATED_NAME" not in line:
                            hits.append(f"{os.path.relpath(path, SRC)}:{n}")
        self.assertEqual(hits, [])

    def test_database(self):
        pattern = re.compile("|".join(MISSPELT), re.IGNORECASE)
        self.assertEqual([n for n in database_names() if pattern.search(n)], [])


class TestOldNamesStillWork(unittest.TestCase):
    def test_adjustment_factor(self):
        for module in (models, geo_models):
            with self.subTest(tree=module.__name__):
                f = module.Land_Use_Features("ireland").get_landuse_features_in_land_use_features_data_base
                self.assertEqual(f("Adjustment_factor", "cropland"), 0.69)
                with self.assertWarns(DeprecationWarning):
                    self.assertEqual(f("Adjustement_factor", "cropland"), 0.69)

    def test_slam_urban_types(self):
        e = geo_models.Nutrient_Exports("ireland")
        for new, old, p in (("continuous_fabric", "continuos_fabric", 1.4),
                            ("discontinuous_fabric", "discontinuos_fabric", 0.86)):
            with self.subTest(type=new):
                self.assertEqual(e.get_P_export_factor_in_export_factor_data_base("urban", new), p)
                self.assertEqual(e.get_N_export_factor_in_export_factor_data_base("urban", new), 5.0)
                with self.assertWarns(DeprecationWarning):
                    self.assertEqual(e.get_P_export_factor_in_export_factor_data_base("urban", old), p)

    def test_new_names_do_not_warn(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            models.Land_Use_Features("ireland").get_landuse_features_in_land_use_features_data_base(
                "Adjustment_factor", "grassland")


if __name__ == "__main__":
    unittest.main()

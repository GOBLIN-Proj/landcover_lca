"""N2O factors for drained organic soils (EF2 dossier).

The database stores these factors as published, in kg N2O-N per ha per year; Emissions_Factors converts them to
kg N2O (x 44/28, landcover_lca.resource_manager.units). Each is checked against the NID 2026 value and against
the CRT 2026 (Tables 3.D and 4(II)).
Run from landcover_lca/tests:  python -m unittest n2o_drainage_factors_test.py
"""
import os
import sqlite3
import unittest

import pandas as pd

import landcover_lca.models as models
from landcover_lca.models import Emissions_Factors

N2O_N_to_N2O = 44.0 / 28.0
CRT = pd.read_csv("./data/inventory/crt2026_n2o_drainage.csv")
DB = os.path.join(os.path.dirname(models.__file__), "database", "landcover_lca_database.db")

# column: (published kg N2O-N/ha/yr, where)
PUBLISHED = {
    "ef_n2o_grassland_drainage_poor": (4.3, "NID 2026 s.5.6.1 p.183, Table 5.6 (IPCC 2013 Wetlands Suppl. Table 2.5)"),
    "ef_n2o_grassland_drainage_rich": (8.2, "NID 2026 s.5.6.1 p.183, Table 5.6 (IPCC 2013 Wetlands Suppl. Table 2.5)"),
    "ef_n2o_forest_drainage_rich": (2.8, "NID 2026 s.6.3 p.220 (IPCC 2013 Wetlands Suppl. Table 2.5)"),
    "ef_n2o_forest_drainage_poor": (0.7, "NID 2026 s.6.3 p.220 (Yamulki et al. 2013)"),
    "ef_n2o_wetland_drainage_default": (0.3, "NID 2026 s.6.6 p.280 (IPCC 2013 Wetlands Suppl., peat extraction)"),
}
UNIT = "kg N2O-N/ha/yr"


def value(name):
    return Emissions_Factors("ireland").get_emission_factor_in_emission_factor_data_base(name)


class TestN2ODrainageFactors(unittest.TestCase):
    def test_calculations_receive_published_n2o_n_times_44_28(self):
        for name, (n2o_n, where) in PUBLISHED.items():
            with self.subTest(name=name):
                self.assertAlmostEqual(value(name), n2o_n * N2O_N_to_N2O, places=6, msg=where)

    def test_units_label_says_kg_n2o_n_per_ha_per_year(self):
        con = sqlite3.connect(DB)
        cur = con.execute("select * from emission_factors_land_use")
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
        con.close()
        unit_row = [r for r in rows if r[0] == "units"][0]
        for name in PUBLISHED:
            with self.subTest(name=name):
                self.assertEqual(unit_row[cols.index(name)], UNIT)

    def test_database_holds_the_published_n2o_n_value(self):
        ef = Emissions_Factors("ireland")
        for name, (n2o_n, where) in PUBLISHED.items():
            with self.subTest(name=name):
                self.assertEqual(ef.get_published_factor(name), (n2o_n, UNIT), msg=where)


class TestAgainstCRT(unittest.TestCase):
    def test_crt_converts_n2o_n_to_n2o_with_44_28(self):
        for _, r in CRT.iterrows():
            with self.subTest(row=r.row, year=r.year):
                kt = r.area_kha * r.ef_kg_n2o_n_per_ha * N2O_N_to_N2O / 1000.0
                self.assertAlmostEqual(kt, r.n2o_kt, places=6)

    def test_peat_extraction_factor_is_the_crt_factor(self):
        peat = CRT[(CRT.crt_table == "Table4(II)") & CRT.row.str.contains("Peat")]
        for ef in peat.ef_kg_n2o_n_per_ha:
            self.assertAlmostEqual(ef * N2O_N_to_N2O, value("ef_n2o_wetland_drainage_default"), places=6)

    def test_grassland_database_factors_reproduce_crt_for_the_crt_rich_share(self):
        # CRT 2022: 141 kha at 6.052 kg N2O-N/ha is a mix of poor (4.3) and rich (8.2): solve the rich share,
        # then the database factors must give the CRT N2O for that mix.
        r = CRT[(CRT.crt_table == "Table3.D") & (CRT.year == 2022)].iloc[0]
        rich = (r.ef_kg_n2o_n_per_ha - 4.3) / (8.2 - 4.3)
        kg = r.area_kha * 1000 * (
            rich * value("ef_n2o_grassland_drainage_rich") + (1 - rich) * value("ef_n2o_grassland_drainage_poor")
        )
        self.assertAlmostEqual(kg / 1e6, r.n2o_kt, places=6)
        self.assertAlmostEqual(rich, 0.449, places=3)


if __name__ == "__main__":
    unittest.main()

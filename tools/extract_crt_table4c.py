"""Extract the mineral-soil rows of CRT Table 4.C (Grassland) from the EPA CRT yearly workbooks.

Reads IRL-CRT-<submission>-V1.0-<year>.xlsx (one workbook per inventory year, sheet 'Table4.C') and writes
one row per year for:
    4.C.1  Grassland remaining grassland   (mineral soils)
    4.C.2  Land converted to grassland     (mineral soils; in Ireland this is forest land only, 4.C.2.a)
Columns used (CRT layout, 0-based): 3 total area (kha), 4 mineral area (kha),
10 implied net C stock change in mineral soils (t C/ha, CRT sign: + gain, - loss),
16 net C stock change in mineral soils (kt C, CRT sign).
Output sign convention (package): + emission, - removal. kg CO2/ha = -(t C/ha) x 1000 x 44/12.

A second output (optional) lists the mineral-soil carbon stock change of all forest-conversion destinations that have
mineral soil rows (4.C.2.a grassland, 4.E.2.a settlements, 4.F.2.a other land), used to cross-check NID Table 6.19.

A third output (optional) is CRT Table 4(III) row 4(III).C.2.a (N2O from N mineralised with the loss of soil carbon,
forest land converted to grassland), used for D5.

Usage: python tools/extract_crt_table4c.py <dir with the yearly workbooks> <submission> <out.csv> [<out_forest_conversions.csv> [<out_4iii_n2o.csv>]]
Example: python tools/extract_crt_table4c.py artifacts/data/national-inventory-2026/IRL-CRT-2026-V1.0 2026 \
             tests/data/inventory/crt2026_4c_mineral_soils.csv tests/data/inventory/crt2026_forest_conversions_mineral_soils.csv
"""
import glob
import re
import sys
import warnings

import openpyxl
import pandas as pd

warnings.filterwarnings("ignore")
C_TO_CO2 = 44.0 / 12.0
ROWS = {"4.C.1.": "4.C.1 Grassland remaining grassland", "4.C.2.": "4.C.2 Land converted to grassland"}


def extract(folder, submission):
    out = []
    for path in sorted(glob.glob(f"{folder}/IRL-CRT-{submission}-V1.0-*.xlsx")):
        year = int(re.search(r"-(\d{4})\.xlsx$", path).group(1))
        ws = openpyxl.load_workbook(path, read_only=True, data_only=True)["Table4.C"]
        for r in ws.iter_rows(min_row=8, max_row=20, values_only=True):
            label = str(r[1] or "").strip()
            for key, name in ROWS.items():
                if label.startswith(key) and not label.startswith(key + "a"):
                    total, mineral, tc_ha, kt_c = r[3], r[4], r[10], r[16]
                    area = mineral if isinstance(mineral, (int, float)) else total
                    if not all(isinstance(v, (int, float)) for v in (area, tc_ha, kt_c)):
                        continue  # 'NO' (not occurring) in this year
                    out.append({
                        "submission": submission, "year": year, "category": name,
                        "mineral_area_kha": area, "soil_tC_per_ha_yr_crt_sign": tc_ha, "mineral_soil_ktC_crt_sign": kt_c,
                        "kgCO2_per_ha_yr": -tc_ha * 1000 * C_TO_CO2, "mineral_soil_ktCO2": -kt_c * C_TO_CO2,
                        "source": f"EPA CRT {submission} Table4.C, row '{label[:45]}', workbook year {year}",
                    })
    return pd.DataFrame(out).sort_values(["category", "year"])


FOREST_ROWS = (("Table4.C", "4.C.2.a", "grassland"), ("Table4.E", "4.E.2.a", "settlement"), ("Table4.F", "4.F.2.a", "other"))


def extract_forest_conversions(folder, submission):
    out = []
    for path in sorted(glob.glob(f"{folder}/IRL-CRT-{submission}-V1.0-*.xlsx")):
        year = int(re.search(r"-(\d{4})\.xlsx$", path).group(1))
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        for sheet, key, dest in FOREST_ROWS:
            for r in wb[sheet].iter_rows(min_row=8, max_row=40, values_only=True):
                label = str(r[1] or "").strip()
                if label.startswith(key):
                    area, kt_c = r[3], r[16]
                    out.append({"submission": submission, "year": year, "destination": dest,
                                "area_kha": area if isinstance(area, (int, float)) else 0.0,
                                "mineral_soil_ktC_crt_sign": kt_c if isinstance(kt_c, (int, float)) else 0.0,
                                "source": f"EPA CRT {submission} {sheet}, row '{label[:40]}', workbook year {year}"})
    return pd.DataFrame(out).sort_values(["destination", "year"])


def extract_4iii_forest_to_grassland(folder, submission):
    """CRT Table4(III), row 4(III).C.2.a. Columns: C area (kha), D N mineralised (t N/yr), G direct, H indirect, I total (kt N2O)."""
    out = []
    for path in sorted(glob.glob(f"{folder}/IRL-CRT-{submission}-V1.0-*.xlsx")):
        year = int(re.search(r"-(\d{4})\.xlsx$", path).group(1))
        ws = openpyxl.load_workbook(path, read_only=True, data_only=True)["Table4(III)"]
        for r in ws.iter_rows(min_row=8, max_row=40, values_only=True):
            if str(r[1] or "").strip().startswith("4(III).C.2.a"):
                num = lambda v: v if isinstance(v, (int, float)) else 0.0
                out.append({"submission": submission, "year": year, "area_kha": num(r[2]), "n_mineralised_t_n": num(r[3]),
                            "direct_kt_n2o": num(r[6]), "indirect_kt_n2o": num(r[7]), "total_kt_n2o": num(r[8]),
                            "source": f"EPA CRT {submission} Table4(III), row 4(III).C.2.a, workbook year {year}"})
    return pd.DataFrame(out).sort_values("year")


if __name__ == "__main__":
    folder, submission, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    df = extract(folder, submission)
    df.to_csv(out, index=False)
    print(df.groupby("category").year.agg(["min", "max", "count"]))
    if len(sys.argv) > 4:
        fc = extract_forest_conversions(folder, submission)
        fc.to_csv(sys.argv[4], index=False)
        print(fc.groupby("destination").year.agg(["min", "max", "count"]))
    if len(sys.argv) > 5:
        n2o = extract_4iii_forest_to_grassland(folder, submission)
        n2o.to_csv(sys.argv[5], index=False)
        print(n2o[["year", "n_mineralised_t_n", "total_kt_n2o"]].tail(5))

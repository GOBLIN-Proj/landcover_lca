"""Extract the inventory test fixtures (activity data and emissions) from the EPA CRT/CRF workbooks.

Writes, into tests/data/inventory/:
    crt2026_lulucf.csv      CRT 2026 cells for 2020-2024 (one row per year and key): Table4, Table4.A-D,
                            Table4(II), Table4(IV). Every row records sheet, row number, row label and column.
    crf2024_burnt_area.csv  CRF 2024 Table4(V) area burnt (ha) for 2020-2022, by land use. The CRT 2026 leaves
                            area burnt blank, and NID 2026 Table 6.8 stops at CRT year 2020 (its labels are four
                            years late), so this is the only published area for these years.

Each cell is located by (sheet, row number, column) and the row label is checked against the expected text,
so a layout change raises instead of reading the wrong row. CRT notation keys (NO, IE, NA, NE, ...) are kept as text.

Usage (from the repo root):
    .venv/bin/python tools/extract_inventory_fixtures.py \
        artifacts/data/national-inventory-2026/IRL-CRT-2026-V1.0 \
        artifacts/data/NIR/NIR_2024/IRL_2024__12032024_130024_started \
        tests/data/inventory
"""
import glob
import os
import sys
import warnings

import openpyxl
import pandas as pd

warnings.filterwarnings("ignore")

CRT_YEARS = range(2020, 2025)
CRF_YEARS = range(2020, 2023)

# column letter -> 0-based index
COL = {c: i for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTU")}

# key: (sheet, row, expected label start, {quantity: (column, unit)})
T4 = {"CO2": ("C", "kt CO2"), "CH4": ("D", "kt CH4"), "N2O": ("E", "kt N2O")}
T4II = {
    "area": ("D", "kha"), "ief_co2": ("E", "kg CO2/ha"), "ief_n2o_n": ("F", "kg N2O-N/ha"), "ief_ch4": ("G", "kg CH4/ha"),
    "CO2": ("H", "kt CO2"), "N2O": ("I", "kt N2O"), "CH4": ("J", "kt CH4"),
}
T4IV = {"CO2": ("J", "kt CO2"), "CH4": ("K", "kt CH4"), "N2O": ("L", "kt N2O")}
SOIL_A = {"area": ("D", "kha"), "mineral_area": ("E", "kha"), "organic_area": ("F", "kha"),
          "mineral_soil_C": ("S", "kt C (CRT sign: + gain)"), "organic_soil_C": ("T", "kt C (CRT sign: + gain)"),
          "net_CO2": ("U", "kt CO2")}
SOIL = {"area": ("D", "kha"), "mineral_area": ("E", "kha"), "organic_area": ("F", "kha"),
        "mineral_soil_C": ("Q", "kt C (CRT sign: + gain)"), "organic_soil_C": ("R", "kt C (CRT sign: + gain)"),
        "net_CO2": ("S", "kt CO2")}

CRT_SPEC = {
    # Table4: totals by category and gas
    "T4.total": ("Table4", 10, "4. Total LULUCF", T4),
    "T4.A.1": ("Table4", 12, "4.A.1.", T4),
    "T4.A.2": ("Table4", 13, "4.A.2.", T4),
    "T4.B.1": ("Table4", 15, "4.B.1.", T4),
    "T4.B.2": ("Table4", 16, "4.B.2.", T4),
    "T4.C.1": ("Table4", 18, "4.C.1.", T4),
    "T4.C.2": ("Table4", 19, "4.C.2.", T4),
    "T4.D.1": ("Table4", 21, "4.D.1.", T4),
    "T4.D.2": ("Table4", 22, "4.D.2.", T4),
    "T4.E.1": ("Table4", 24, "4.E.1.", T4),
    "T4.E.2": ("Table4", 25, "4.E.2.", T4),
    "T4.F.1": ("Table4", 27, "4.F.1.", T4),
    "T4.F.2": ("Table4", 28, "4.F.2.", T4),
    "T4.G": ("Table4", 29, "4.G.", T4),
    # areas and soil carbon
    "A.total": ("Table4.A", 10, "4.A. Total forest land", SOIL_A),
    "A.1": ("Table4.A", 11, "4.A.1.", SOIL_A),
    "A.2": ("Table4.A", 12, "4.A.2.", SOIL_A),
    "B.1": ("Table4.B", 11, "4.B.1.", SOIL),
    "C.1": ("Table4.C", 11, "4.C.1.", SOIL),
    "D.1": ("Table4.D", 11, "4.D.1.", SOIL),
    "D.1.a": ("Table4.D", 12, "4.D.1.a.", SOIL),
    "D.domestic": ("Table4.D", 13, "Domestic Peat Extraction", SOIL),
    "D.industrial": ("Table4.D", 14, "Industrial Peat Extraction", SOIL),
    "D.rewetted_industrial": ("Table4.D", 15, "Rewetted Industrial Peat Extraction", SOIL),
    "D.other_domestic": ("Table4.D", 16, "Other Domestic Peat Extraction", SOIL),
    "D.near_natural": ("Table4.D", 19, "Near Natural Wetlands", SOIL),
    "D.unmanaged": ("Table4.D", 20, "Unmanaged Wetlands", SOIL),
    # Table4(II): drainage and rewetting of organic soils
    "II.A.1.drained": ("Table4(II)", 14, "Drained organic soils", T4II),
    "II.A.2.drained": ("Table4(II)", 18, "Drained organic soils", T4II),
    "II.C.1.drained": ("Table4(II)", 30, "Drained organic soils", T4II),
    "II.C.1.other": ("Table4(II)", 33, "Other organic soils", T4II),
    "II.D.domestic": ("Table4(II)", 47, "Domestic Peat Extraction", T4II),
    "II.D.industrial": ("Table4(II)", 48, "Industrial Peat Extraction", T4II),
    "II.D.rewetted_industrial": ("Table4(II)", 50, "Rewetted Industrial Peat Extraction", T4II),
    "II.D.other_domestic": ("Table4(II)", 52, "Other Domestic Peat Extraction", T4II),
    "II.D.near_natural": ("Table4(II)", 75, "Near Natural Wetlands", T4II),
    # Table4(IV): biomass burning (all reported as wildfires)
    "IV.A.1": ("Table4(IV)", 14, "4(IV).A.1.b. Wildfires", T4IV),
    "IV.A.2": ("Table4(IV)", 17, "4(IV).A.2.b. Wildfires", T4IV),
    "IV.B.1": ("Table4(IV)", 21, "4(IV).B.1.b. Wildfires", T4IV),
    "IV.C.1": ("Table4(IV)", 28, "4(IV).C.1.b. Wildfires", T4IV),
    "IV.D.1": ("Table4(IV)", 35, "4(IV).D.1.b. Wildfires", T4IV),
}

# CRF 2024 Table4(V): area burnt (column E, ha). Label in column A.
CRF_SPEC = {
    "forest_remaining": (12, "Wildfires", 10, "1. Forest land remaining"),
    "land_converted_to_forest": (15, "Wildfires", 13, "2. Land converted to forest"),
    "cropland": (17, "1.  Cropland remaining cropland", None, None),
    "grassland": (24, "1. Grassland remaining grassland", None, None),
    "wetland": (31, "1. Wetlands remaining wetlands", None, None),
}


def _label(row, col="B"):
    return str(row[COL[col]] or "").strip()


def _value(v):
    if isinstance(v, (int, float)):
        return float(v), ""
    return None, str(v).strip() if v is not None else ""


def extract_crt(folder):
    out = []
    for year in CRT_YEARS:
        path = os.path.join(folder, f"IRL-CRT-2026-V1.0-{year}.xlsx")
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        cache = {}
        for key, (sheet, rnum, expect, quantities) in CRT_SPEC.items():
            if sheet not in cache:
                cache[sheet] = {i: r for i, r in enumerate(wb[sheet].iter_rows(min_row=1, max_row=110, values_only=True), start=1)}
            row = cache[sheet][rnum]
            label = _label(row)
            if not label.startswith(expect):
                raise ValueError(f"{year} {sheet} row {rnum}: expected '{expect}', found '{label}'")
            for quantity, (col, unit) in quantities.items():
                value, notation = _value(row[COL[col]])
                out.append(dict(year=year, key=key, quantity=quantity, value=value, notation=notation, unit=unit,
                                sheet=sheet, row=rnum, label=label, column=col,
                                source=f"EPA CRT 2026 {sheet} row {rnum} col {col}, workbook year {year}"))
    return pd.DataFrame(out)


def extract_crf_burnt(folder):
    out = []
    for year in CRF_YEARS:
        path = glob.glob(os.path.join(folder, f"IRL_2024_{year}_*.xlsx"))[0]
        ws = openpyxl.load_workbook(path, read_only=True, data_only=True)["Table4(V)"]
        rows = {i: r for i, r in enumerate(ws.iter_rows(min_row=1, max_row=40, values_only=True), start=1)}
        for key, (rnum, expect, parent, parent_expect) in CRF_SPEC.items():
            label = _label(rows[rnum], "A")
            if not label.startswith(expect):
                raise ValueError(f"{year} Table4(V) row {rnum}: expected '{expect}', found '{label}'")
            if parent and not _label(rows[parent], "A").startswith(parent_expect):
                raise ValueError(f"{year} Table4(V) row {parent}: expected '{parent_expect}'")
            if rows[rnum][COL["D"]] != "ha":
                raise ValueError(f"{year} Table4(V) row {rnum}: unit is not ha")
            value, notation = _value(rows[rnum][COL["E"]])
            out.append(dict(year=year, land_use=key, area_burnt_ha=value, notation=notation,
                            source=f"EPA CRF 2024 (submission 2024) Table4(V) row {rnum} col E ('{label}'), workbook year {year}"))
    return pd.DataFrame(out)


def main(crt_folder, crf_folder, out_folder):
    crt = extract_crt(crt_folder)
    crt.to_csv(os.path.join(out_folder, "crt2026_lulucf.csv"), index=False)
    crf = extract_crf_burnt(crf_folder)
    crf.to_csv(os.path.join(out_folder, "crf2024_burnt_area.csv"), index=False)
    print(f"crt2026_lulucf.csv: {len(crt)} rows; crf2024_burnt_area.csv: {len(crf)} rows")


if __name__ == "__main__":
    main(*sys.argv[1:4])

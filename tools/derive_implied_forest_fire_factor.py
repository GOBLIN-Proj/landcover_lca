"""Derive the forest wildfire implied factors (FIRE-1) from the committed inventory fixtures.

    factor (kg per ha burnt) = sum over the years of CRT 2026 Table 4(IV) 4.A.1 + 4.A.2 wildfire emissions (kt x 1e6)
                               / sum over the years of CRF 2024 Table4(V) area burnt, 4.A.1 + 4.A.2 (ha)

The CRT 2026 leaves area burnt blank, so the previous submission's area (CRF 2024) is used; it covers 2020-2022.
Pooling (sum / sum) weights each year by its burnt area. Fixtures: tests/data/inventory/crt2026_lulucf.csv and
crf2024_burnt_area.csv (tools/extract_inventory_fixtures.py).

Usage (from the repo root):
    .venv/bin/python tools/derive_implied_forest_fire_factor.py           # print the factors
    .venv/bin/python tools/derive_implied_forest_fire_factor.py --write   # also write them to the database

--write sets the value of ef_{co2,ch4,n2o}_implied_wildfire_forest in the factor table
data/emission_factors_land_use.csv and writes that table into the database
(tools/write_emission_factors.py).
"""
import csv
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import write_emission_factors  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INV = os.path.join(ROOT, "tests", "data", "inventory")

YEARS = (2020, 2021, 2022)
COLUMNS = {
    "CO2": "ef_co2_implied_wildfire_forest",
    "CH4": "ef_ch4_implied_wildfire_forest",
    "N2O": "ef_n2o_implied_wildfire_forest",
}


def derive():
    crt = pd.read_csv(os.path.join(INV, "crt2026_lulucf.csv"))
    burnt = pd.read_csv(os.path.join(INV, "crf2024_burnt_area.csv"))
    area = burnt[burnt.year.isin(YEARS) & burnt.land_use.isin(["forest_remaining", "land_converted_to_forest"])]
    if len(area) != 2 * len(YEARS) or area.area_burnt_ha.isna().any():
        raise ValueError("burnt area missing for a year")
    ha = float(area.area_burnt_ha.sum())
    out = {}
    for gas in COLUMNS:
        e = crt[crt.year.isin(YEARS) & crt.key.isin(["IV.A.1", "IV.A.2"]) & (crt.quantity == gas)]
        if len(e) != 2 * len(YEARS) or e.value.isna().any():
            raise ValueError(f"CRT {gas} missing for a year")
        out[gas] = float(e.value.sum()) * 1e6 / ha
    return out, ha


def write(factors):
    rows = write_emission_factors.read_csv()
    by_name = {r["name"]: r for r in rows}
    for gas, name in COLUMNS.items():
        if by_name[name]["unit"] != f"kg {gas}/ha burnt":
            raise ValueError(f"{name}: unexpected unit {by_name[name]['unit']!r}")
        by_name[name]["value"] = repr(factors[gas])
    with open(write_emission_factors.CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["name", "value", "unit", "source"], lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    write_emission_factors.write()


if __name__ == "__main__":
    factors, ha = derive()
    print(f"burnt area 2020-2022: {ha:.2f} ha")
    for gas, value in factors.items():
        print(f"{COLUMNS[gas]}: {value:.4f} kg {gas} per ha burnt")
    if "--write" in sys.argv[1:]:
        write(factors)
        print(f"written to {write_emission_factors.CSV} and {write_emission_factors.DB}")

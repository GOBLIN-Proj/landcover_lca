"""Derive the forest wildfire implied factors (FIRE-1) from the committed inventory fixtures.

    factor (kg per ha burnt) = sum over the years of CRT 2026 Table 4(IV) 4.A.1 + 4.A.2 wildfire emissions (kt x 1e6)
                               / sum over the years of CRF 2024 Table4(V) area burnt, 4.A.1 + 4.A.2 (ha)

The CRT 2026 leaves area burnt blank, so the previous submission's area (CRF 2024) is used; it covers 2020-2022.
Pooling (sum / sum) weights each year by its burnt area. Fixtures: tests/data/inventory/crt2026_lulucf.csv and
crf2024_burnt_area.csv (tools/extract_inventory_fixtures.py).

Usage (from the repo root):
    .venv/bin/python tools/derive_implied_forest_fire_factor.py           # print the factors
    .venv/bin/python tools/derive_implied_forest_fire_factor.py --write   # also write them to the database

--write sets the value, source and units cells of ef_{co2,ch4,n2o}_implied_wildfire_forest in
emission_factors_land_use. Columns still spelt with the old names (ef_*_implied_wilfire_forest) are renamed first.
"""
import os
import sqlite3
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INV = os.path.join(ROOT, "tests", "data", "inventory")
DB = os.path.join(ROOT, "src", "landcover_lca", "database", "landcover_lca_database.db")

YEARS = (2020, 2021, 2022)
COLUMNS = {
    "CO2": ("ef_co2_implied_wilfire_forest", "ef_co2_implied_wildfire_forest"),
    "CH4": ("ef_CH4_implied_wilfire_forest", "ef_ch4_implied_wildfire_forest"),
    "N2O": ("ef_n2o_implied_wilfire_forest", "ef_n2o_implied_wildfire_forest"),
}
SOURCE = ("CRT 2026 Table 4(IV).A.1 + A.2 wildfire emissions / CRF 2024 Table4(V) area burnt (4.A.1 + 4.A.2), "
          "2020-2022, sum/sum (docs/emission_factor_provenance.md)")


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
    con = sqlite3.connect(DB)
    present = {r[1] for r in con.execute("pragma table_info(emission_factors_land_use)")}
    for gas, (old, new) in COLUMNS.items():
        if old in present:
            con.execute(f"alter table emission_factors_land_use rename column [{old}] to [{new}]")
        rows = {"ireland": factors[gas], "source": SOURCE, "units": f"kg {gas} per ha burnt"}
        for country, value in rows.items():
            cur = con.execute(f"update emission_factors_land_use set [{new}] = ? where ef_country = ?", (value, country))
            if cur.rowcount != 1:
                raise ValueError(f"{new}: row {country} not found")
    con.commit()
    con.close()


if __name__ == "__main__":
    factors, ha = derive()
    print(f"burnt area 2020-2022: {ha:.2f} ha")
    for gas, value in factors.items():
        print(f"{COLUMNS[gas][1]}: {value:.4f} kg {gas} per ha burnt")
    if "--write" in sys.argv[1:]:
        write(factors)
        print(f"written to {DB}")

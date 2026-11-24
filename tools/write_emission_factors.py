"""Write data/emission_factors_land_use.csv into the database.

The CSV is the readable record of the tables (the database is binary in git): one row per factor with the value and
unit as published and the source. This rebuilds the table emission_factors_land_use from it, in the same long
format: one row per country and factor (ef_country TEXT, name TEXT, value REAL, unit TEXT, source TEXT), all
rows with ef_country 'ireland'.

Every unit must be listed in landcover_lca.resource_manager.units.UNITS. tests/units_test.py checks that the
database equals the CSV.

To change a factor: edit the CSV, run this, run the tests.

Usage (from the repo root):
    .venv/bin/python tools/write_emission_factors.py
"""
import csv
import os
import sqlite3

from landcover_lca.resource_manager.units import UNITS
from landcover_lca.database import get_database_path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE = os.path.join(ROOT, "src", "landcover_lca", "database")
DB = get_database_path()  # landcover_lca.database.DATABASE_FILE
CSV = os.path.join(ROOT, "data", "emission_factors_land_use.csv")  # repository only, not shipped


def read_csv(path=CSV):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def write(path=CSV, db=DB):
    rows = read_csv(path)
    names = [r["name"] for r in rows]
    if len(set(names)) != len(names):
        raise ValueError("duplicate factor names in the CSV")
    for r in rows:
        if r["unit"] not in UNITS:
            raise ValueError(f"{r['name']}: unit {r['unit']!r} not in units.UNITS")
    con = sqlite3.connect(db)
    with con:
        con.execute("drop table if exists emission_factors_land_use")
        con.execute("create table emission_factors_land_use (ef_country TEXT NOT NULL, name TEXT NOT NULL, "
                    "value REAL NOT NULL, unit TEXT NOT NULL, source TEXT NOT NULL, PRIMARY KEY (ef_country, name))")
        con.executemany("insert into emission_factors_land_use values ('ireland', ?, ?, ?, ?)",
                        [(r["name"], float(r["value"]), r["unit"], r["source"]) for r in rows])
    con.execute("vacuum")
    con.close()
    return len(rows)


if __name__ == "__main__":
    print(f"wrote {write()} factors to {DB}")

"""Write src/landcover_lca/database/emission_factors_land_use.csv into the database table emission_factors_land_use.

The CSV is the readable record of the table (the database is binary in git): one row per factor with the value and
unit as published and the source. This writes the three database rows 'ireland' (value), 'units' and 'source'.
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
CSV = os.path.join(DATABASE, "emission_factors_land_use.csv")


def read_csv(path=CSV):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def write(path=CSV, db=DB):
    rows = read_csv(path)
    con = sqlite3.connect(db)
    present = {r[1] for r in con.execute("pragma table_info(emission_factors_land_use)")} - {"ef_country"}
    names = {r["name"] for r in rows}
    if names != present:
        raise ValueError(f"CSV and database columns differ: only in CSV {sorted(names - present)}, "
                         f"only in database {sorted(present - names)}")
    for r in rows:
        if r["unit"] not in UNITS:
            raise ValueError(f"{r['name']}: unit {r['unit']!r} not in units.UNITS")
        for country, value in (("ireland", float(r["value"])), ("units", r["unit"]), ("source", r["source"])):
            cur = con.execute(f"update emission_factors_land_use set [{r['name']}] = ? where ef_country = ?",
                              (value, country))
            if cur.rowcount != 1:
                raise ValueError(f"{r['name']}: row {country} not found")
    con.commit()
    con.close()
    return len(rows)


if __name__ == "__main__":
    print(f"wrote {write()} factors to {DB}")

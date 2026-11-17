"""Derive ef_co2_implied_grassland_remaining_SOC_per_ha from the stored CRF extract.

The NID publishes only totals for CRF 4.C.1 (Grassland remaining grassland, mineral soils), not a
per-hectare factor, so the factor is derived:

    factor (kg CO2/ha/yr) = sum of kt CO2 over the years / sum of mineral area (kha) over the years x 1000

Pooling kt and area (rather than averaging the yearly ratios) weights each year by its area.
Sign: negative = removal. Source rows: tests/data/inventory/crf_4c1_grassland_remaining_mineral.csv
(EPA CRF Table 4.C). To refresh: replace that file with the newer submission, change the
arguments, re-run, update the database value and docs/emission_factor_provenance.md.

Usage (from the repo root):
    python tools/derive_implied_grassland_factor.py [submission first_year last_year]
"""
import sys

import pandas as pd

DEFAULT_CSV = "tests/data/inventory/crf_4c1_grassland_remaining_mineral.csv"


def derive(csv_path, submission, first_year, last_year):
    d = pd.read_csv(csv_path)
    w = d[(d.submission == submission) & d.year.between(first_year, last_year)]
    expected = last_year - first_year + 1
    if len(w) != expected:
        raise ValueError(f"expected {expected} years for submission {submission}, found {len(w)}")
    kt = float(w.mineral_soil_ktCO2.sum())
    area = float(w.mineral_area_kha.sum())
    return {
        "submission": submission, "first_year": first_year, "last_year": last_year,
        "years": expected, "sum_kt_co2": kt, "sum_area_kha": area,
        "kgCO2_per_ha_yr": kt / area * 1000.0,
        "yearly_kgCO2_per_ha_yr": dict(zip(w.year.astype(int), w.kgCO2_per_ha_yr.round(2))),
    }


if __name__ == "__main__":
    sub, a, b = (int(x) for x in sys.argv[1:4]) if len(sys.argv) >= 4 else (2025, 2019, 2023)
    r = derive(DEFAULT_CSV, sub, a, b)
    print(f"{r['submission']} submission, {a}-{b}: sum {r['sum_kt_co2']:.2f} kt CO2 / {r['sum_area_kha']:.2f} kha"
          f" = {r['kgCO2_per_ha_yr']:.6f} kg CO2/ha/yr")
    print("yearly:", r["yearly_kgCO2_per_ha_yr"])

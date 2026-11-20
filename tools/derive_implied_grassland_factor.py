"""Derive the implied mineral-soil factors from the stored CRT extract (tests/data/inventory/crt2026_4c_mineral_soils.csv).

  4.C.1  -> ef_co2_implied_grassland_remaining_SOC_per_ha   (Grassland remaining grassland)
  4.C.2  -> ef_co2_implied_forest_to_grassland_SOC_per_ha   (Land converted to grassland: forest only in Ireland)

The NID publishes only totals for 4.C.1, not a per-hectare factor, so the factor is derived:

    factor (kg CO2/ha/yr) = sum of kt CO2 over the years / sum of mineral area (kha) over the years x 1000

Pooling kt and area (rather than averaging the yearly ratios) weights each year by its area.
Sign: negative = removal. Source rows: tests/data/inventory/crf_4c1_grassland_remaining_mineral.csv
(EPA CRT Table 4.C, written by tools/extract_crt_table4c.py). To refresh: re-extract the newer
submission, change the arguments, re-run, update the database value and docs/emission_factor_provenance.md.

Usage (from the repo root):
    python tools/derive_implied_grassland_factor.py [submission first_year last_year]   (prints both factors)
"""
import sys

import pandas as pd

DEFAULT_CSV = "tests/data/inventory/crt2026_4c_mineral_soils.csv"


def derive(csv_path, submission, first_year, last_year, category="4.C.1"):
    d = pd.read_csv(csv_path)
    w = d[(d.submission == submission) & d.category.str.startswith(category) & d.year.between(first_year, last_year)]
    expected = last_year - first_year + 1
    if len(w) != expected:
        raise ValueError(f"expected {expected} years of {category} for submission {submission}, found {len(w)}")
    kt = float(w.mineral_soil_ktCO2.sum())
    area = float(w.mineral_area_kha.sum())
    return {
        "submission": submission, "first_year": first_year, "last_year": last_year,
        "years": expected, "sum_kt_co2": kt, "sum_area_kha": area,
        "kgCO2_per_ha_yr": kt / area * 1000.0,
        "yearly_kgCO2_per_ha_yr": dict(zip(w.year.astype(int), w.kgCO2_per_ha_yr.round(2))),
    }


if __name__ == "__main__":
    sub, a, b = (int(x) for x in sys.argv[1:4]) if len(sys.argv) >= 4 else (2026, 2020, 2024)
    for cat, name in (("4.C.1", "ef_co2_implied_grassland_remaining_SOC_per_ha"), ("4.C.2", "ef_co2_implied_forest_to_grassland_SOC_per_ha")):
        r = derive(DEFAULT_CSV, sub, a, b, cat)
        print(f"{name}: {r['submission']} submission, {a}-{b}: sum {r['sum_kt_co2']:.2f} kt CO2 / "
              f"{r['sum_area_kha']:.2f} kha = {r['kgCO2_per_ha_yr']:.6f} kg CO2/ha/yr")
        print("   yearly:", r["yearly_kgCO2_per_ha_yr"])

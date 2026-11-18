"""Build landcover_lca inputs from the national inventory (NID/CRT 2026), for tests/inventory_alignment_test.py.

The package is given the inventory's own areas, so its results can be compared with the CRT 2026 emissions.
Nothing here depends on landcover_assignment. Fixtures (all in data/inventory/, each row carries its source):
    crt2026_lulucf.csv               CRT 2026 cells, 2020-2024 (tools/extract_inventory_fixtures.py)
    crf2024_burnt_area.csv           CRF 2024 Table4(V) area burnt, 2020-2022 (same tool)
    nid2026_forest_organic_soils.csv NID 2026 Tables 6.7 and 6.15, transcribed (drained N-poor / N-rich areas)

How each land use is built (area_ha in ha; shares are fractions of area_ha):
    forest     area = CRT 4.A total (4.A.1 + 4.A.2). share_mineral = 4.A mineral / total.
               share_organic (package "poor") = NID drained N-poor (organic) area, 4.A.1 + 4.A.2.
               share_organic_mineral (package "rich") = NID drained N-rich (organo-mineral) area, 4.A.1 + 4.A.2.
               The NID excludes open areas (roads, rides) from the drained area; CRT 4(II) reports the organic
               area including them, so the CRT implied factors per ha are lower than the per-ha factors.
    grassland  area = CRT 4.C.1. share_mineral = 4.C.1 mineral / total.
               Drained organic = CRT 4(II) "Drained organic soils" (136.6 kha in 2020).
               "Other organic soils" (203.3 kha) = the package's "rewetted" grassland: NID 2026 s.6.5.2
               (p.271-272) describes them as previously drained land "in some form of rewet status", charged with
               the same factors the package holds for rewetted grassland (on-site 0.85 / 0.5 t C, DOC 0.24 t C,
               CH4 68.1 / 216 kg CH4-C). This is not deliberate rewetting.
               The NID publishes no rich/poor area split for grassland (Hammond 1981, not tabulated). The split is
               DERIVED from the CRT CH4 implied factor of each row with the package's own CH4 factors, so the
               grassland CH4 comparison is a consistency check, not an independent test.
    wetland    area = CRT 4.D.1 (peat extraction + near-natural + unmanaged). Shares from the CRT 4(II) areas:
               domestic and industrial peat extraction (drained), rewetted industrial, near-natural; unmanaged from 4.D.
               4(II) and 4.D split the peat-extraction areas differently (2020: industrial 55.5 kha in 4(II),
               98.3 kha in 4.D). The 4(II) areas are used. "Other Domestic Peat Extraction" has no package category
               (share 0; a known gap).
    cropland   area = CRT 4.B.1, all mineral.
    burnt      share_burnt = CRF 2024 area burnt / area (2020-2022 only; 0 in other years). Forest = 4.A.1 + 4.A.2.

The transition matrix holds only "remaining" areas and no conversions, and past = current (span 0), so every
land-use-change term is 0. Conversions are tested in soc_test, soc_inventory_test and soc_n2o_test.
Wetland_to_Wetland is 0 because Wetland.co2_removals fails for a non-zero value (W1).
"""
import inspect
import os

import pandas as pd

from landcover_lca.models import Emissions_Factors, load_land_use_data, load_transition_matrix

HERE = os.path.dirname(os.path.abspath(__file__))
INV = os.path.join(HERE, "data", "inventory")

CRT = pd.read_csv(os.path.join(INV, "crt2026_lulucf.csv"))
BURNT = pd.read_csv(os.path.join(INV, "crf2024_burnt_area.csv"))
NID_FOREST = pd.read_csv(os.path.join(INV, "nid2026_forest_organic_soils.csv"))

YEARS = list(range(2020, 2025))
FIRE_YEARS = sorted(BURNT.year.unique())
KHA = 1000.0
C_TO_CO2 = 44.0 / 12.0

SHARE_COLUMNS = [
    "share_mineral", "share_organic", "share_drained_rich_organic", "share_drained_poor_organic",
    "share_rewetted_rich_organic", "share_rewetted_poor_organic", "share_organic_mineral",
    "share_rewetted_in_organic", "share_rewetted_in_mineral", "share_domestic_peat_extraction",
    "share_industrial_peat_extraction", "share_rewetted_industrial_peat_extraction",
    "share_rewetted_domestic_peat_extraction", "share_near_natural_wetland", "share_unmanaged_wetland",
    "share_burnt",
]
LAND_USES = ["grassland", "wetland", "cropland", "forest", "settlement", "farmable_condition"]


def crt(year, key, quantity):
    """CRT value; notation keys (NO, IE, ...) read as 0."""
    row = CRT[(CRT.year == year) & (CRT.key == key) & (CRT.quantity == quantity)]
    if len(row) != 1:
        raise KeyError((year, key, quantity))
    v = row.value.iloc[0]
    return 0.0 if pd.isna(v) else float(v)


def burnt_ha(year, *land_uses):
    rows = BURNT[(BURNT.year == year) & BURNT.land_use.isin(land_uses)]
    return float(rows.area_burnt_ha.fillna(0).sum())


def factor(name):
    return Emissions_Factors("ireland").get_emission_factor_in_emission_factor_data_base(name)


def grassland_rich_fraction(year):
    """Rich fraction of drained and of 'other' (rewet status) grassland organic soil, from the CRT CH4 implied factors."""
    ditch = factor("frac_ditch")
    ch4_ditch = factor("ef_ch4_grassland_drainage_ditch")
    poor = (1 - ditch) * factor("ef_ch4_grassland_drainage_land_poor") + ditch * ch4_ditch
    rich = (1 - ditch) * factor("ef_ch4_grassland_drainage_land_rich") + ditch * ch4_ditch
    drained = (crt(year, "II.C.1.drained", "ief_ch4") - poor) / (rich - poor)
    rw_poor, rw_rich = factor("ef_ch4_grassland_rewetting_poor"), factor("ef_ch4_grassland_rewetting_rich")
    other = (crt(year, "II.C.1.other", "ief_ch4") - rw_poor) / (rw_rich - rw_poor)
    return drained, other


def _row(year, land_use, area_ha, **shares):
    row = {"farm_id": -year, "year": year, "land_use": land_use, "area_ha": area_ha}
    row.update({c: 0.0 for c in SHARE_COLUMNS})
    for k, v in shares.items():
        if k not in SHARE_COLUMNS:
            raise KeyError(k)
        row[k] = v / area_ha if area_ha else 0.0
    return row


def inventory_land_use_frame(year):
    """The package's land-use table for one inventory year (areas in ha; shares as fractions)."""
    fire = year in FIRE_YEARS
    rows = []

    # forest
    f_area = crt(year, "A.total", "area") * KHA
    nid = NID_FOREST[NID_FOREST.year == year]
    rows.append(_row(year, "forest", f_area,
                     share_mineral=crt(year, "A.total", "mineral_area") * KHA,
                     share_organic=nid.drained_organic_poor_kha.sum() * KHA,
                     share_organic_mineral=nid.drained_organo_mineral_rich_kha.sum() * KHA,
                     share_burnt=burnt_ha(year, "forest_remaining", "land_converted_to_forest") if fire else 0.0))

    # grassland
    g_area = crt(year, "C.1", "area") * KHA
    rich_dr, rich_other = grassland_rich_fraction(year)
    drained = crt(year, "II.C.1.drained", "area") * KHA
    other = crt(year, "II.C.1.other", "area") * KHA
    rows.append(_row(year, "grassland", g_area,
                     share_mineral=crt(year, "C.1", "mineral_area") * KHA,
                     share_organic=crt(year, "C.1", "organic_area") * KHA,
                     share_drained_rich_organic=drained * rich_dr,
                     share_drained_poor_organic=drained * (1 - rich_dr),
                     share_rewetted_rich_organic=other * rich_other,
                     share_rewetted_poor_organic=other * (1 - rich_other),
                     share_burnt=burnt_ha(year, "grassland") if fire else 0.0))

    # wetland
    w_area = crt(year, "D.1", "area") * KHA
    rows.append(_row(year, "wetland", w_area,
                     share_organic=w_area,
                     share_domestic_peat_extraction=crt(year, "II.D.domestic", "area") * KHA,
                     share_industrial_peat_extraction=crt(year, "II.D.industrial", "area") * KHA,
                     share_rewetted_industrial_peat_extraction=crt(year, "II.D.rewetted_industrial", "area") * KHA,
                     share_near_natural_wetland=crt(year, "II.D.near_natural", "area") * KHA,
                     share_unmanaged_wetland=crt(year, "D.unmanaged", "area") * KHA,
                     share_burnt=burnt_ha(year, "wetland") if fire else 0.0))

    # cropland
    c_area = crt(year, "B.1", "area") * KHA
    rows.append(_row(year, "cropland", c_area, share_mineral=c_area,
                     share_burnt=burnt_ha(year, "cropland") if fire else 0.0))

    rows.append(_row(year, "settlement", 0.0))
    rows.append(_row(year, "farmable_condition", 0.0))
    return pd.DataFrame(rows)


def inventory_transition_frame(year, land_use_frame):
    """Remaining areas only, no conversions (Wetland_to_Wetland = 0, see W1)."""
    names = ["Grassland", "Wetland", "Cropland", "Forest", "Settlement", "Farmable_Condition"]
    area = dict(zip(land_use_frame.land_use, land_use_frame.area_ha))
    cols = {f"{a}_to_{b}": 0.0 for a in names for b in names}
    for n in ("Grassland", "Cropland", "Forest"):
        cols[f"{n}_to_{n}"] = area[n.lower()]
    return pd.DataFrame([cols], index=[-year])


def inventory_inputs(year):
    """Return (land_use, past_land_use, transition_matrix) as loaded package objects; past = current (span 0)."""
    frame = inventory_land_use_frame(year)
    data = load_land_use_data(frame, year)
    tm = load_transition_matrix(inventory_transition_frame(year, frame), "ireland", year, year)
    return data[-year], data[-year], tm[-year]


ARG_NAMES = {
    "ef_country": "ef_country",
    "land_use": "land_use", "land_use_data": "land_use",
    "past_land_use_data": "past", "past_land_use": "past",
    "transition_matrix": "tm", "transition_matrix_data": "tm",
    "year": "year", "calibration_year": "year",  # horticulture_co2_peat_export: the inventory year itself
}


def run(function, year):
    """Call a landcover_lca per-term function by argument name (the module uses three argument orders). Result in kg."""
    land_use, past, tm = inventory_inputs(year)
    values = {"ef_country": "ireland", "land_use": land_use, "past": past, "tm": tm, "year": year}
    params = inspect.signature(function).parameters
    return function(**{p: values[ARG_NAMES[p]] for p in params})

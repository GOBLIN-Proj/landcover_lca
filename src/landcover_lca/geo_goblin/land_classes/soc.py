"""
Soil organic carbon (mineral soils) for the geo tree: the national tree's SOC class (D8, option C).

There is one implementation, ``landcover_lca.land_classes.soc.SOC``, so the fixes made there (D1 closed form for any
span, D3 clear error for a missing transition, D4a LAC 85 t C/ha for cropland transitions, D6 checked years) and any
later fix apply to geo_goblin too. It returns t C per year; the CO2 and N2O functions, also shared
(``landcover_lca.lca_emission``, imported by ``geo_lca_emissions``), convert to kg CO2 and kg N2O. It reads the same
database through the same loader, and works with the geo_models land-use and transition objects.
"""
from landcover_lca.land_classes.soc import SOC  # noqa: F401

__all__ = ["SOC"]

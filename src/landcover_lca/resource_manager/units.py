"""Unit conversions for landcover_lca, kept in one place.

The database table ``emission_factors_land_use`` stores every factor **as published** (the number printed in the NID,
CRT or IPCC table, in that source's unit), one row per factor with its ``unit`` and ``source``. ``Emissions_Factors`` converts on read,
using the table below, to the unit the calculations use. So a number in the database can be checked against its
source by eye, and every conversion happens here.

Model units (what the calculations receive):
    soil and stock CO2          kg CO2 per ha (per year for fluxes)
    CH4, N2O per area           kg CH4 / kg N2O per ha per year
    fire emission factors       g gas per kg dry matter burnt
    fuel burnt (MB x Cf)        t dry matter per ha
    implied fire factors        kg gas per ha burnt
    fractions                   dimensionless

To add a factor: store the published value and unit, and cite the source in the ``source`` column
(see docs/emission_factor_provenance.md). If the unit is not listed in UNITS, add it here with its conversion.
"""

# molecular-weight ratios
C_TO_CO2 = 44.0 / 12.0  # t C to t CO2
CH4_C_TO_CH4 = 16.0 / 12.0  # kg CH4-C to kg CH4
N2O_N_TO_N2O = 44.0 / 28.0  # kg N2O-N to kg N2O

# mass
T_TO_KG = 1e3
KT_TO_KG = 1e6

# published unit -> (multiplier to the model unit, model unit)
UNITS = {
    # carbon fluxes and stocks, published as carbon
    "t CO2-C/ha/yr": (T_TO_KG * C_TO_CO2, "kg CO2/ha/yr"),
    "t C/ha": (T_TO_KG * C_TO_CO2, "kg CO2/ha"),
    "t C/t air-dry peat": (C_TO_CO2, "t CO2/t air-dry peat"),
    # published already as CO2 (CRT-derived per-ha factors)
    "kg CO2/ha/yr": (1.0, "kg CO2/ha/yr"),
    # CH4 and N2O per area
    "kg CH4/ha/yr": (1.0, "kg CH4/ha/yr"),
    "kg CH4-C/ha/yr": (CH4_C_TO_CH4, "kg CH4/ha/yr"),
    "kg N2O-N/ha/yr": (N2O_N_TO_N2O, "kg N2O/ha/yr"),
    # fire
    "t dm/ha": (1.0, "t dm/ha"),
    "g CO2/kg dm": (1.0, "g CO2/kg dm"),
    "g CO2-C/kg dm": (C_TO_CO2, "g CO2/kg dm"),
    "g CH4/kg dm": (1.0, "g CH4/kg dm"),
    "g N2O/kg dm": (1.0, "g N2O/kg dm"),
    "kg CO2/ha burnt": (1.0, "kg CO2/ha burnt"),
    "kg CH4/ha burnt": (1.0, "kg CH4/ha burnt"),
    "kg N2O/ha burnt": (1.0, "kg N2O/ha burnt"),
    # dimensionless
    "fraction": (1.0, "fraction"),
}


def to_model_units(value, unit, name=""):
    """Convert a published factor to the unit the calculations use. Raises KeyError for an unlisted unit."""
    if unit not in UNITS:
        raise KeyError(f"{name}: unit {unit!r} is not in landcover_lca.resource_manager.units.UNITS")
    return float(value) * UNITS[unit][0]


def model_unit(unit):
    """The unit a published unit is converted to."""
    return UNITS[unit][1]

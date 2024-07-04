from landcover_lca.geo_goblin.geo_models import Nutrient_Exports

def main():
    ef_country = "ireland"

    nutrient_exports = Nutrient_Exports(ef_country)


    type = "conifer"
    landuse = "forest"

    print(nutrient_exports.get_N_export_factor_in_export_factor_data_base(landuse, type))

    print(nutrient_exports.get_P_export_factor_in_export_factor_data_base(landuse, type))

if __name__ == "__main__":
    main()
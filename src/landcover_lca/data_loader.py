from landcover_lca.database_manager import DataManager



class Loader:
    def __init__(self, ef_country):
        self.dataframes = DataManager(ef_country)


    def land_use_features(self):
        return self.dataframes.get_landuse_features()
    

    def landuse_emissions_factors(self):
        return self.dataframes.get_landuse_emissions_factors()
    
    
    def ipcc_soc_factors(self):
        return self.dataframes.get_ipcc_soc_factors()
    

    def national_forest_inventory(self):
        return self.dataframes.get_national_forest_inventory()
    

    def exported_peat(self):
        return self.dataframes.get_exported_peat()
import sqlalchemy as sqa
import pandas as pd
from landcover_lca.database import get_local_dir
import os


class DataManager:
    def __init__(self, ef_country):
        self.database_dir = get_local_dir()
        self.engine = self.data_engine_creater()
        self.ef_country = ef_country

    def data_engine_creater(self):
        database_path = os.path.abspath(
            os.path.join(self.database_dir, "landcover_lca_database.db")
        )
        engine_url = f"sqlite:///{database_path}"

        return sqa.create_engine(engine_url)

    def get_landuse_features(self):
        table = "land_use_features"
        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["land_use"],
        )

        return dataframe

    def get_landuse_emissions_factors(self):
        table = "emission_factors_land_use"
        dataframe = pd.read_sql(
            "SELECT * FROM '%s' WHERE ef_country = '%s'" % (table, self.ef_country),
            self.engine,
            index_col=["ef_country"],
        )

        return dataframe

    def get_ipcc_soc_factors(self):
        table = "ipcc_soil_class_SOC"
        dataframe = pd.read_sql(
            "SELECT * FROM '%s' WHERE ef_country = '%s'" % (table, self.ef_country),
            self.engine,
            index_col=["ef_country"],
        )

        return dataframe

    def get_national_forest_inventory(self):
        table = "national_forest_inventory_2017"
        dataframe = pd.read_sql("SELECT * FROM '%s'" % (table), self.engine)

        return dataframe

    def get_exported_peat(self):
        table = "UN_comtrade_exported_peat"
        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["Year"],
        )

        return dataframe

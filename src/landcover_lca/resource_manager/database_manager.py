"""
Description:
    This module contains the DataManager class, a tool for managing and retrieving various datasets 
    related to landcover_lca tool. The class is designed to interact with a SQL database using SQLAlchemy,
    providing methods to fetch land use features, land use emissions factors, IPCC soil class SOC factors, national forest 
    inventory data, and exported peat data. It is optimized for ease of use and efficiency.

Note: 
    This is part of a larger suite of tools developed for environmental data analysis and modeling. 

"""


import sqlalchemy as sqa
import pandas as pd
from landcover_lca.database import get_local_dir
import os


class DataManager:
    """
    A class that manages the database operations for landcover LCA.

    Attributes:
        database_dir (str): The directory path of the database.
        engine (sqlalchemy.engine.Engine): The SQLAlchemy engine for database connection.
        ef_country (str): The country for which the emissions factors are retrieved.

    Methods:
        __init__(ef_country): Initializes the DataManager object.
        data_engine_creater(): Creates and returns the SQLAlchemy engine for database connection.
        get_landuse_features(): Retrieves the land use features from the database.
        get_landuse_emissions_factors(): Retrieves the land use emissions factors from the database.
        get_ipcc_soc_factors(): Retrieves the IPCC soil class SOC factors from the database.
        get_national_forest_inventory(): Retrieves the national forest inventory data from the database.
        get_exported_peat(): Retrieves the exported peat data from the database.
        get_slam_export_data(): Retrieves the SLAM export data from the database.
    """

    def __init__(self, ef_country):
        """
        Initializes the DataManager object.

        Args:
            ef_country (str): The country for which the emissions factors are retrieved.
        """
        self.database_dir = get_local_dir()
        self.engine = self.data_engine_creater()
        self.ef_country = ef_country

    def data_engine_creater(self):
        """
        Creates and returns the SQLAlchemy engine for database connection.

        Returns:
            sqlalchemy.engine.Engine: The SQLAlchemy engine for database connection.
        """
        database_path = os.path.abspath(
            os.path.join(self.database_dir, "landcover_lca_database.db")
        )
        engine_url = f"sqlite:///{database_path}"

        return sqa.create_engine(engine_url)

    def get_landuse_features(self):
        """
        Retrieves the land use features from the database.

        Returns:
            pandas.DataFrame: The land use features data.
        """
        table = "land_use_features"
        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["land_use"],
        )

        return dataframe

    def get_landuse_emissions_factors(self):
        """
        Retrieves the land use emissions factors from the database.

        Returns:
            pandas.DataFrame: The land use emissions factors data.
        """
        table = "emission_factors_land_use"
        dataframe = pd.read_sql(
            "SELECT * FROM '%s' WHERE ef_country = '%s'" % (table, self.ef_country),
            self.engine,
            index_col=["ef_country"],
        )

        return dataframe

    def get_ipcc_soc_factors(self):
        """
        Retrieves the IPCC soil class SOC factors from the database.

        Returns:
            pandas.DataFrame: The IPCC soil class SOC factors data.
        """
        table = "ipcc_soil_class_SOC"
        dataframe = pd.read_sql(
            "SELECT * FROM '%s' WHERE ef_country = '%s'" % (table, self.ef_country),
            self.engine,
            index_col=["ef_country"],
        )

        return dataframe

    def get_national_forest_inventory(self):
        """
        Retrieves the national forest inventory data from the database.

        Returns:
            pandas.DataFrame: The national forest inventory data.
        """
        table = "national_forest_inventory_2017"
        dataframe = pd.read_sql("SELECT * FROM '%s'" % (table), self.engine)

        return dataframe

    def get_exported_peat(self):
        """
        Retrieves the exported peat data from the database.

        Returns:
            pandas.DataFrame: The exported peat data.
        """
        table = "UN_comtrade_exported_peat"
        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,
            index_col=["Year"],
        )

        return dataframe
    
    def get_slam_export_data(self):
        """
        Retrieves the SLAM export data from the database.

        Returns:
            pandas.DataFrame: The SLAM export data.
        """
        table = "slam_nutrient_export_rates"
        dataframe = pd.read_sql(
            "SELECT * FROM '%s'" % (table),
            self.engine,  
            index_col=["ef_country"],
        )

        return dataframe

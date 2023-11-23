"""
Description: 

    This file contains the Loader class, which is responsible for loading various datasets related to land cover life cycle assessment.

    The Loader class is designed to provide easy access to different types of environmental data, such as land use features, emissions factors, IPCC SOC factors, national forest inventory, and exported peat. This is achieved through an instance of the DataManager class, which manages the actual data retrieval processes.

    The Loader class serves as an interface for accessing these datasets, abstracting the underlying data management complexities. It is typically used in environmental assessment and modeling projects that require comprehensive and diverse datasets related to land cover and its impact.

Note:
    This class is part of a larger suite of tools developed for environmental life cycle assessment and modeling, and it relies on the DataManager class from the landcover_lca.database_manager module for data management.
"""

from landcover_lca.database_manager import DataManager


class Loader:
    """
    A class that loads data for land cover life cycle assessment.

    Attributes:
        dataframes (DataManager): An instance of the DataManager class for managing data.

    Methods:
        land_use_features: Returns the land use features.
        landuse_emissions_factors: Returns the land use emissions factors.
        ipcc_soc_factors: Returns the IPCC SOC factors.
        national_forest_inventory: Returns the national forest inventory.
        exported_peat: Returns the exported peat.
    """

    def __init__(self, ef_country):
        """
        Initializes a Loader object.

        Parameters:
            ef_country (str): The country for which the data is loaded.
        """
        self.dataframes = DataManager(ef_country)

    def land_use_features(self):
        """
        Returns the land use features.

        Returns:
            pandas.DataFrame: The land use features.
        """
        return self.dataframes.get_landuse_features()

    def landuse_emissions_factors(self):
        """
        Returns the land use emissions factors.

        Returns:
            pandas.DataFrame: The land use emissions factors.
        """
        return self.dataframes.get_landuse_emissions_factors()

    def ipcc_soc_factors(self):
        """
        Returns the IPCC SOC factors.

        Returns:
            pandas.DataFrame: The IPCC SOC factors.
        """
        return self.dataframes.get_ipcc_soc_factors()

    def national_forest_inventory(self):
        """
        Returns the national forest inventory.

        Returns:
            pandas.DataFrame: The national forest inventory.
        """
        return self.dataframes.get_national_forest_inventory()

    def exported_peat(self):
        """
        Returns the exported peat.

        Returns:
            pandas.DataFrame: The exported peat.
        """
        return self.dataframes.get_exported_peat()

"""
Description: 
    This file contains classes related to managing and processing environmental or agricultural model data. 

Classes:
    DataManager: Manages and stores various data parameters essential for calibration and modeling processes, such as calibration years, target years, and organic mineral soil depth.

    ModelData: Manages metadata related to land use. It maintains a list of columns relevant for land use data analysis and modeling, including identifiers and various attributes related to land use.

Usage: 
    These classes are integral to scenarios involving environmental or agricultural modeling and land use data processing. They help in standardizing and organizing the necessary parameters and metadata for efficient data handling and analysis.

Note: 
    This is part of a larger suite of tools developed for environmental data analysis and modeling. 
"""


class DataManager:
    def __init__(self, calibration_year=None, target_year=None):
        """
        DataManager is a class designed to manage and store various data parameters essential for calibration and modeling processes.

        Attributes:
            calibration_year (int, optional): The year used for calibration. If not provided, a default year is used.
            default_calibration_year (int): The default year used for calibration if no specific year is provided. Set to 2015.
            target_year (int, optional): The target year for which the model data is relevant. This could be a future or past year depending on the model's context.
            organic_mineral_soil_depth (int): Represents the depth of organic mineral soil, set to a default value of 28 (units not specified in the class definition but could be in centimeters or inches depending on the model's context).

        Methods:
            get_calibration_year: Returns the calibration year.
            get_default_calibration_year: Returns the default calibration year.
            get_target_year: Returns the target year.
            get_organic_mineral_soil_depth: Returns the depth of organic mineral soil.

        Usage:
            This class can be used in scenarios where calibration and target years are important for modeling processes, especially in environmental or agricultural models. It also stores a standard value for organic mineral soil depth, which might be a parameter in soil-related calculations.


        """
        self.calibration_year = calibration_year
        self.default_calibration_year = 2015
        self.target_year = target_year
        self.organic_mineral_soil_depth = 28

    def get_calibration_year(self):
        """
        Returns the calibration year.

        Returns:
            int: The year used for calibration.
        """
        return self.calibration_year
    
    def get_default_calibration_year(self):
        """
        Returns the default calibration year.

        Returns:
            int: The default year used for calibration if no specific year is provided.
        """
        return self.default_calibration_year
    
    def get_target_year(self):
        """
        Returns the target year.

        Returns:
            int: The target year for the model data.
        """
        return self.target_year
    
    def get_organic_mineral_soil_depth(self):
        """
        Returns the depth of organic mineral soil.

        Returns:
            int: The depth of organic mineral soil.
        """
        return self.organic_mineral_soil_depth


class ModelData:
    """
    ModelData is a class designed to store and manage metadata related to land use. Primarily, it maintains a list of columns that are relevant for land use data analysis and modeling.

    Attributes:
        land_use_columns (list of str): A list containing the names of columns that are important for land use data. These columns typically include identifiers and various attributes related to land use, such as area, shares of different land types, etc.

    Methods:
        get_land_use_columns: Returns the list of land use columns.
        
    Usage:
        This class is particularly useful in scenarios involving data processing or analysis of land use, where a consistent set of columns is required to standardize data frames or databases for further analysis.

    """

    def __init__(self):
        self.land_use_columns = [
            "farm_id",
            "year",
            "area_ha",
            "share_organic",
            "share_mineral",
            "share_rewetted_in_organic",
            "share_burnt",
            "share_rewetted_in_mineral",
            "share_peat_extraction",
        ]

    def get_land_use_columns(self):
        """
        Returns the list of land use columns.

        Returns:
            list of str: A list containing the names of columns that are important for land use data.
        """
        return self.land_use_columns
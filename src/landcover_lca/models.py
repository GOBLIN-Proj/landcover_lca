"""
Description:
    This file, part of a larger environmental analysis toolkit, contains the implementation of various models and algorithms 
    central to the study and assessment of environmental impacts. These models are for simple data processing. 

    The file is structured to provide a modular and reusable approach to 
    model implementation, facilitating easy integration with other components of the toolkit.

Note: 
    This is part of a larger suite of tools developed for environmental data analysis and modeling. 

"""

import pandas as pd
from landcover_lca.resource_manager.data_loader import Loader
from landcover_lca.resource_manager.landcover_data_manager import ModelData


###########################################
class DynamicData:
    """
    DynamicData is a utility class designed for managing data with an emphasis on overriding default values with real data, if available.
    This class is typically used as a base class for other classes such as Land_Use_Category and LandUseCollections.

    Initialization:
        DynamicData(data, defaults={})

    Parameters:
        data (dict): A dictionary containing the real data. Each key-value pair in this dictionary represents a data attribute and its value.
        defaults (dict, optional): A dictionary of default values. Defaults to an empty dictionary.
            Each key-value pair represents a default attribute and its value.

    Description:
        Upon initialization, DynamicData first sets all attributes based on the 'defaults' dictionary.
        If the same attributes are present in the 'data' dictionary, the default values are overwritten with the values from 'data'.
        This ensures that all attributes have values, using defaults when real data is not available.

    Usage:
        The class is typically used as a superclass. Derived classes inherit the functionality of initializing and managing
        data with default and real values.

    Example:
        class Land_Use_Category(DynamicData):
            pass

        category_data = {"name": "Residential", "code": 100}
        default_values = {"name": "Unknown", "code": 0}

        category = Land_Use_Category(category_data, default_values)

        In this example, Land_Use_Category inherits from DynamicData. When an instance of Land_Use_Category is created,
        it contains the real data if available; otherwise, it falls back to the default values.
    """

    def __init__(self, data, defaults={}):
        # Set the defaults first
        for variable, value in defaults.items():
            setattr(self, variable, value)

        # Overwrite the defaults with the real values
        for variable, value in data.items():
            setattr(self, variable, value)


class Land_Use_Category(DynamicData):
    """
    Land_Use_Category is a subclass of DynamicData, specialized in handling data related to land use categories.
    It initializes with a set of default values for various land use attributes, and these defaults can be overridden with actual data.

    The class primarily deals with attributes like farm ID, year, land use type, area in hectares, and various shares related
    to land use such as mineral, organic, rewetted, burnt, and peat extraction.

    Initialization:
        Land_Use_Category(data, calibration_year)

    Parameters:
        data (dict): A dictionary containing the actual data for land use categories. Each key-value pair in this dictionary
            should correspond to a land use attribute and its value.
        calibration_year (int): The year used for calibration, which sets the default year value for land use.

    Default Values:
        The class initializes the following default values:
        - farm_id: 0
        - year: The year provided in calibration_year
        - land_use: 'no'
        - area_ha: 0
        - share_mineral: 0
        - share_organic: 0
        - share_rewetted_in_organic: 0
        - share_burnt: 0
        - share_rewetted_in_mineral: 0
        - share_peat_extraction: 0

    Usage:
        This class can be used to create instances representing different land use categories, with the flexibility to
        input actual data or rely on default settings.

    Example:
        land_use_data = {"farm_id": 123, "land_use": "agriculture"}
        category = Land_Use_Category(land_use_data, 2022)

        In this example, an instance of Land_Use_Category is created with specific data for a farm, and the default
        values are used for unspecified attributes.
    """

    def __init__(self, data, calibration_year):
        defaults = {
            "farm_id": 0,
            "year": calibration_year,
            "land_use": "no",
            "area_ha": 0,
            "share_mineral": 0,
            "share_organic": 0,
            "share_rewetted_in_organic": 0,
            "share_burnt": 0,
            "share_rewetted_in_mineral": 0,
            "share_peat_extraction": 0,
        }

        super().__init__(data, defaults)


class LandUseCollection(DynamicData):

    """
    LandUseCollection is a subclass of DynamicData, designed to handle collections of land use data. Unlike the Land_Use_Category class,
    this class does not utilize default values for its data attributes. It inherits the core functionality of DynamicData to manage
    its data attributes solely based on the input data provided.

    The primary use of this class, along with Land_Use_Category, is within the load_land_use_data() function, where it serves to organize
    and manage collections of land use data items.

    Initialization:
        LandUseCollection(data)

    Parameters:
        data (dict): A dictionary containing the land use data. Each key-value pair in this dictionary represents an attribute of the
        land use collection and its corresponding value.

    Usage:
        This class is intended to aggregate and manage multiple instances or items of land use data. It is particularly useful in scenarios
        where a collection of land use data items needs to be processed or manipulated as a single entity.

    Example:
        land_use_items = [{"farm_id": 1, "land_use": "agriculture"}, {"farm_id": 2, "land_use": "forestry"}]
        land_use_collection = LandUseCollection(land_use_items)

        In this example, LandUseCollection is instantiated with a list of land use data dictionaries. Each item in the list represents
        a separate land use data point. The LandUseCollection instance manages these as a collective group of data items.
    """

    def __init__(self, data):
        super().__init__(data)


class TransitionData:
    """
    TransitionData is a class similar to DynamicData, but it specifically manages transition data.
    It initializes with default values and overrides them with actual data if available. The primary distinction
    lies in its handling of certain data types, specifically converting values to integers or floats as needed.

    This class is designed to be inherited by other classes, such as TransitionMatrixCategory, to provide a
    standardized way of handling transition data across different categories.

    Initialization:
        TransitionData(data, defaults={})

    Parameters:
        data (dict): A dictionary containing the actual transition data. Each key-value pair in this dictionary
            represents a transition attribute and its value.
        defaults (dict, optional): A dictionary of default values for transition data attributes. Defaults to an empty dictionary.
            Each key-value pair represents a default transition attribute and its value.

    Special Handling:
        - If the variable is "Year" or "farm_id", the value is converted to an integer.
        - For other variables, values are converted to integers after being interpreted as floats.

    Usage:
        This class is intended to be used for managing transition data, where default values are provided and can
        be overridden by actual data. It's particularly useful in scenarios requiring data type conversions for
        specific fields like "Year" and "farm_id".

    Example:
        transition_data = {"Year": "2022", "farm_id": "100", "area_ha": "250.5"}
        default_values = {"Year": 0, "farm_id": 0, "area_ha": 0}
        transition_instance = TransitionData(transition_data, default_values)

        In this example, a TransitionData instance is created with specific data, where numerical values are
        properly converted and defaults are used for unspecified attributes.
    """

    def __init__(self, data, defaults={}):
        # Set the defaults first
        for variable, value in defaults.items():
            setattr(self, variable, value)

        # Overwrite the defaults with the real values
        for variable, value in data.items():
            if variable == "Year":
                setattr(self, "Year", int(float(value)))
            elif variable == "farm_id":
                setattr(self, "farm_id", int(float(value)))
            else:
                setattr(self, variable.lower(), int(float(value)))


class TransitionMatrixCategory(TransitionData):
    """
    TransitionMatrixCategory is a subclass of TransitionData, specifically tailored for managing transition matrix data related to different categories.
    It inherits the functionality of TransitionData, with the addition of category-specific default values.

    This class is primarily used for initializing transition data with a set of default values that are relevant to a particular category,
    such as country, farm_id, year, land use, and area in hectares. These defaults can be overridden with actual data.

    Initialization:
        TransitionMatrixCategory(data, ef_country, calibration_year)

    Parameters:
        data (dict): A dictionary containing the actual data for the transition matrix category.
            Each key-value pair in this dictionary represents an attribute of the category and its value.
        ef_country (str): A string representing the default value for the country attribute in the transition matrix category.
        calibration_year (int): An integer representing the default value for the Year attribute in the transition matrix category.

    Default Values:
        The class initializes the following default values:
        - country: The value provided in ef_country
        - farm_id: 0
        - Year: The year provided in calibration_year
        - land_use: 'no'
        - area_ha: 0

    Usage:
        This class is used to manage transition matrix data for different categories, allowing for the easy setup of default values
        and the ability to override them with actual data. It is useful in scenarios where data consistency and type conversion
        are important for transition matrices.

    Example:
        transition_category_data = {"farm_id": 123, "land_use": "agriculture", "area_ha": "250.5"}
        category = TransitionMatrixCategory(transition_category_data, "ireland", 2022)

        In this example, a TransitionMatrixCategory instance is created with specific data for a farm in the ireland for the year 2022.
        The default values are used for unspecified attributes while ensuring the proper data type conversions.
    """

    def __init__(self, data, ef_country, calibration_year):
        defaults = {
            "country": ef_country.lower(),
            "farm_id": 0,
            "Year": calibration_year,
            "land_use": "no",
            "area_ha": 0,
        }

        super(TransitionMatrixCategory, self).__init__(data, defaults)


class Emissions_Factors:
    """
    Emissions_Factors is a class designed to interact with a land use database to read and retrieve emissions factors data.
    It is initialized with a specific country's context and utilizes a data loading mechanism to access the emissions factors.

    The primary functionality of this class is to provide an interface for retrieving emissions factor values based on
    given emissions factor names, tailored to the specified country.

    Initialization:
        Emissions_Factors(ef_country)

    Parameters:
        ef_country (str): A string specifying the country context for which the emissions factors data is to be loaded and used.

    Attributes:
        data_loader_class (Loader): An instance of the Loader class initialized with the ef_country, responsible for loading the emissions factors data.
        ef_country (str): The country context for the emissions factors.
        emission_data_base (dict): A dictionary containing emissions factors data loaded from the land use database.

    Methods:
        get_emission_factor_in_emission_factor_data_base(emission_factor_name)
            - Retrieves the emission factor value for a specified emission factor name, within the context of the ef_country.
            - Parameters:
                emission_factor_name (str): The name of the emission factor whose value is to be retrieved.
            - Returns:
                float: The value of the specified emission factor for the given country.

    Usage:
        This class can be used to access and retrieve specific emissions factors from a land use database,
        particularly in environmental impact assessments or similar analyses where emissions data is crucial.

    Example:
        emissions_factors = Emissions_Factors("ireland")
        co2_emission_factor = emissions_factors.get_emission_factor_in_emission_factor_data_base("emission_factor_name")

        In this example, an instance of Emissions_Factors is created for the ireland. The CO2 emissions factor for the ireland is then retrieved using the class method.
    """

    def __init__(self, ef_country):
        self.ef_country = ef_country.lower()
        self.data_loader_class = Loader(self.ef_country)
        self.emission_data_base = self.data_loader_class.landuse_emissions_factors()


    def get_emission_factor_in_emission_factor_data_base(self, emission_factor_name):
        return float(
            self.emission_data_base.get(emission_factor_name).get(self.ef_country)
        )


class Land_Use_Features:
    """
    Land_Use_Features is a class designed to interact with a land use database to read and retrieve National Inventory soil adjustment data.
    It is initialized with a specific country's context and utilizes a data loading mechanism to access the land use features.

    The primary functionality of this class is to provide an interface for retrieving land use feature values based on
    given land use feature names, tailored to specific land use types.

    Initialization:
        Land_Use_Features(ef_country)

    Parameters:
        ef_country (str): A string specifying the country context for which the land use features data is to be loaded and used.

    Attributes:
        data_loader_class (Loader): An instance of the Loader class initialized with the ef_country, responsible for loading the land use features data.
        features_data_base (dict): A dictionary containing land use features data loaded from the land use database.

    Methods:
        get_landuse_features_in_land_use_features_data_base(emission_feature_name, land_use):
            - Retrieves the land use feature value for a specified feature name and land use type, within the context of the specified country.
            - Parameters:
                emission_feature_name (str): The name of the land use feature whose value is to be retrieved.
                land_use (str): The land use type for which the feature value is relevant.
            - Returns:
                float: The value of the specified land use feature for the given land use type.

    Usage:
        This class can be used to access and retrieve specific land use features from a land use database,
        particularly in environmental assessments or similar analyses where land use data is crucial.

    Example:
        land_use_features = Land_Use_Features("ireland")
        soil_adjustment_factor = land_use_features.get_landuse_features_in_land_use_features_data_base("Adjustment_factor", "cropland")

        In this example, an instance of Land_Use_Features is created for the ireland. The soil adjustment factor for cropland land use in ireland is then retrieved using the class method.
    """

    def __init__(self, ef_country):
        self.ef_country = ef_country.lower()
        self.data_loader_class = Loader(self.ef_country)
        self.features_data_base = self.data_loader_class.land_use_features()

    def get_landuse_features_in_land_use_features_data_base(
        self, emission_feature_name, land_use
    ):
        return float(self.features_data_base.get(emission_feature_name).get(land_use))


def load_land_use_data(land_use_data_frame, calibration_year):
    """
    Processes and organizes land use data from a given DataFrame into structured land use categories and collections.

    The function performs three main steps:
    1. Convert all specified columns in the DataFrame to numeric values, facilitating further calculations.
    2. Aggregate the data into individual land use categories based on the data in each row.
    3. Group these categories into collections based on farm IDs, organizing them under a unified structure.

    Parameters:
        land_use_data_frame (DataFrame): A pandas DataFrame containing land use data with various columns.
        calibration_year (int): The year used for calibration, influencing how data is processed and categorized.

    Returns:
        dict: A dictionary where each key is a farm ID and each value is a LandUseCollection object representing all land uses associated with that farm.

    Steps:
        1. Numeric Conversion: Converts columns specified by the ModelData class into numeric values, handling non-numeric values gracefully.
        2. Category Creation: Iterates through the DataFrame, creating a Land_Use_Category object for each row with the provided calibration year.
        3. Collection Aggregation: Aggregates these categories into collections based on farm IDs.
        4. Collection Object Creation: Converts the raw data into LandUseCollection objects, each representing all land uses under a single farm ID.

    Usage:
        This function is used to process raw land use data, making it structured and easily manageable for further analysis or processing.
        It is particularly useful in scenarios where land use data needs to be categorized and grouped for large datasets.

    Example:
        land_use_df = pd.DataFrame([...])  # a pandas DataFrame with land use data
        processed_data = load_land_use_data(land_use_df, 2022)

        In this example, the function takes a DataFrame of land use data and the calibration year 2022,
        and returns a dictionary of LandUseCollection objects organized by farm IDs.
    """
    data_manager_class = ModelData()

    cols = data_manager_class.get_land_use_columns()

    for column in cols:
        land_use_data_frame[column] = pd.to_numeric(
            land_use_data_frame[column], errors="coerce"
        )

    categories = []  # this will be a list of dictionaries

    for _, row in land_use_data_frame.iterrows():
        data = dict([(x, row.get(x)) for x in row.keys()])
        categories.append(Land_Use_Category(data, calibration_year))

    # 2. Aggregate the categories into collection based on the farm ID

    collections = {}  # farm id is the first key, with nested land use keys

    for category in categories:
        farm_id = int(category.farm_id)  # access farm_id and save to var
        land_use = category.land_use  # access land_use and save to var

        if farm_id not in collections:
            collections[farm_id] = {land_use: category}
        else:
            collections[farm_id][land_use] = category

    # 3. Convert the raw collection data into land use collection objects

    collection_objects = {}  # add all of the land uses under a single farm_id

    for farm_id, raw_data in collections.items():
        collection_objects[farm_id] = LandUseCollection(raw_data)

    return collection_objects


def print_land_use_data(land_use_data):
    """
    Iterates through a nested dictionary of land use data and prints information about each item.

    This function is designed to work with a data structure where the outer dictionary is keyed by scenarios (or similar identifiers),
    and each value is another dictionary containing land use categories. Each land use category object has attributes representing
    various parameters.

    Parameters:
        land_use_data (dict): A nested dictionary where the top-level keys are scenarios or similar identifiers.
            Each corresponding value is a dictionary of land use categories with their respective data.

    Output:
        Prints information about each scenario, land use category, and their parameters to the console.
        The output format is "Scenario: [scenario], Land use: [land_use], parameter: [parameter] = [attribute]".

    Usage:
        This function is useful for debugging or inspecting the land use data structure. It allows for a quick overview of the data
        contained within the structure, printed in a readable format.
    """
    for sc, values in land_use_data.items():
        for land_use, value in values.__dict__.items():
            for parameter, attribute in value.__dict__.items():
                print(
                    f"Scenario: {sc}, Land use: {land_use}, parameter: {parameter} = {attribute}"
                )


def load_transition_matrix(
    transition_matrix_data_frame, ef_country, calibration_year, target_year
):
    """
    Processes and organizes transition matrix data from a given DataFrame into structured transition matrix categories.

    The function performs the following steps:
    1. Converts the 'farm_id' and 'Year' columns and other numeric columns in the DataFrame to numeric values, facilitating further calculations.
    2. Adjusts the 'Year' column values based on the calibration_year and target_year.
    3. Creates TransitionMatrixCategory objects for each row in the DataFrame.
    4. Aggregates these categories into a collection based on farm IDs.

    Parameters:
        transition_matrix_data_frame (DataFrame): A pandas DataFrame containing transition matrix data.
        ef_country (str): A string specifying the country context for the transition matrix data.
        calibration_year (int): The year used for calibration, influencing how data is processed and categorized.
        target_year (int): The target year for which the transition matrix data is relevant.

    Returns:
        dict: A dictionary where each key is a farm ID and the value is a TransitionMatrixCategory object representing the transition data for that farm.

    Steps:
        - Numeric Conversion: Converts columns to numeric values, handling non-numeric values gracefully.
        - Year Adjustment: Adjusts the 'Year' column based on the calibration and target years.
        - Category Creation: Iterates through the DataFrame, creating a TransitionMatrixCategory object for each row.
        - Collection Aggregation: Aggregates these categories into a dictionary keyed by farm IDs.

    Usage:
        This function is used to process raw transition matrix data, making it structured and easily manageable for further analysis or processing.
        It is particularly useful in scenarios where transition matrix data needs to be categorized and grouped for large datasets.

    """
    transition_matrix_data_frame["farm_id"] = transition_matrix_data_frame.index

    for column in transition_matrix_data_frame.columns[1:]:
        if column != "farm_id":
            transition_matrix_data_frame[column] = pd.to_numeric(
                transition_matrix_data_frame[column], errors="coerce"
            )

    transition_matrix_data_frame["Year"] = transition_matrix_data_frame.index.astype(
        int
    )

    transition_matrix_data_frame.loc[
        (transition_matrix_data_frame.loc[:, "Year"] == 0), "Year"
    ] = calibration_year
    transition_matrix_data_frame.loc[
        (transition_matrix_data_frame.loc[:, "Year"] != calibration_year),
        "Year",
    ] = target_year

    # 1. Load each land use category into an object
    transition_categories = []

    for _, row in transition_matrix_data_frame.iterrows():
        data = dict([(x, row.get(x)) for x in row.keys()])
        transition_categories.append(
            TransitionMatrixCategory(data, ef_country, calibration_year)
        )

    # 2. Aggregate the land use categories into collection based on the farm ID

    collections = {}

    for category in transition_categories:
        farm_id = category.farm_id
        collections[farm_id] = category

    return collections


def print_transition_data(transition_data):
    """
    Iterates through a dictionary of transition data and prints information about each item.

    This function is designed to work with a data structure where the outer dictionary is keyed by scenarios (or similar identifiers),
    and each value is an object containing transition data for different land use types.

    Parameters:
        transition_data (dict): A dictionary where the top-level keys are scenarios or similar identifiers.
            Each corresponding value is an object representing transition data for different land uses.

    Output:
        Prints information about each scenario and the corresponding transition data to the console.
        The output format is "Scenario: [scenario], Land use: [land_use] = [value]".

    Usage:
        This function is useful for debugging or inspecting the transition data structure. It allows for a quick overview
        of the data contained within the structure, printed in a readable format.

    """
    for sc, values in transition_data.items():
        for land_use, value in values.__dict__.items():
            print(f"Scenario: {sc}, Land use: {land_use} = {value}")

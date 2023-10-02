import pandas as pd
from landcover_lca.data_loader import Loader
from landcover_lca.landcover_data_manager import ModelData


###########################################
class DynamicData:
    """
    Dynamic Data is a simple class that takes real data and a set of default data. It sets the data to the default data.
    If real data is available, the default data is overridden.

    This class is inherited by the Land_Use_Category and the LandUseCollections classes.

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
    Generates the initial default data using __init__. The class inherits the DynamicData class, the actual data and the defaults data are passed to it.
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
    Serves a similar purpose to the Land_Use_Category class, however, no default data is passed to DynamicData.
    Both the LandUseCollection and Land_use_Category classes are used the load_land_use_data() function.
    """

    def __init__(self, data):
        super().__init__(data)


class TransitionData:
    """
    Serves a similar purpose to the DynamicData class, except in respect to the transition data. It sets the data if real data exists, if not, it uses a default value.

    Class is inherited by TransitionMatrixCategory()
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
    Generates the initial default data using __init__. The class inherits the TransitionData class, the actual data and the defaults data are passed to it.
    """

    def __init__(self, data, ef_country, calibration_year):
        defaults = {
            "country": ef_country,
            "farm_id": 0,
            "Year": calibration_year,
            "land_use": "no",
            "area_ha": 0,
        }

        super(TransitionMatrixCategory, self).__init__(data, defaults)


class Emissions_Factors:
    """
    Reads the emissions factors data from the land use database.

    Implements the get_emission_factor_in_emission_factor_data_base() method to retrieve an
    emissions factor values based on the passed emissions factor name.

    """

    def __init__(self, ef_country):
        self.data_loader_class = Loader(ef_country)
        self.ef_country = ef_country
        self.emission_data_base = self.data_loader_class.landuse_emissions_factors()

    def get_emission_factor_in_emission_factor_data_base(self, emission_factor_name):
        return float(
            self.emission_data_base.get(emission_factor_name).get(self.ef_country)
        )


class Land_Use_Features:
    """
    Reads the National Inventory soil adjustment data from the land use database.

    Implements the get_landuse_features_in_land_use_features_data_base() method to retrieve an
    land use feature values based on the passed land use feature name.

    """

    def __init__(self, ef_country):
        self.data_loader_class = Loader(ef_country)
        self.features_data_base = self.data_loader_class.land_use_features()

    def get_landuse_features_in_land_use_features_data_base(
        self, emission_feature_name, land_use
    ):
        return float(self.features_data_base.get(emission_feature_name).get(land_use))


def load_land_use_data(land_use_data_frame, calibration_year):
    data_manager_class = ModelData()

    cols = data_manager_class.land_use_columns

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
    for sc, values in land_use_data.items():
        for land_use, value in values.__dict__.items():
            for parameter, attribute in value.__dict__.items():
                print(
                    f"Scenario: {sc}, Land use: {land_use}, parameter: {parameter} = {attribute}"
                )


def load_transition_matrix(
    transition_matrix_data_frame, ef_country, calibration_year, target_year
):
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
    for sc, values in transition_data.items():
        for land_use, value in values.__dict__.items():
            print(f"Scenario: {sc}, Land use: {land_use} = {value}")

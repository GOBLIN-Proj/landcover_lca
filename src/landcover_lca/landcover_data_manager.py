class DataManager:
    def __init__(self, calibration_year, target_year):
        self.calibration_year = calibration_year
        self.default_calibration_year = 2015
        self.target_year = target_year


class ModelData:
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

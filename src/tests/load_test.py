import unittest
import pandas as pd
import os

from landcover_lca.models import load_transition_matrix, print_transition_data, load_land_use_data, print_land_use_data


class DatasetLoadingTestCase(unittest.TestCase):
    def setUp(self):
        self.data_dir = "./data"

        self.ef_country = "ireland"
        self.baseline = 2021
        self.target = 2050

        self.transition_matrix = pd.read_csv(os.path.join(self.data_dir, "transition.csv"), index_col = 0)
        self.land_uses = pd.read_csv(os.path.join(self.data_dir, "land_uses.csv"), index_col = 0)

    def test_dataset_loading(self):
        # Test loading the datasets as pandas DataFrames

        
        transition = load_transition_matrix(self.transition_matrix, self.ef_country, self.baseline, self.target)

        print_transition_data(transition)
        
        land = load_land_use_data(self.land_uses, self.baseline)

        print_land_use_data(land)
    
if __name__ == "__main__":
    unittest.main()
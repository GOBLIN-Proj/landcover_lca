from landcover_lca.models import load_transition_matrix, load_land_use_data
import landcover_lca.lca_emission as lca
import pandas as pd
import os
import unittest
from tempfile import TemporaryDirectory


class TestGenerateData(unittest.TestCase):
    def test_generate_scenario_dataframe_creates_file(self):
        # Use a temporary directory
        with TemporaryDirectory() as tmp_dir:
            data_dir = "./data"

            ef_country = "ireland"
            baseline = 2020
            target = 2050

            transition = pd.read_csv(os.path.join(data_dir, "transition.csv"), index_col=0)
            land_uses = pd.read_csv(os.path.join(data_dir, "land_uses.csv"), index_col=0)

            transition_matrix = load_transition_matrix(transition, ef_country, baseline, target)

            land_use_data = load_land_use_data(land_uses, baseline)

            baseline_index = -1
            base = -baseline
        
            emission_df = pd.DataFrame(
                columns=["CO2", "CH4", "N2O", "CO2e"],
                index=pd.MultiIndex.from_product(
                    [
                        # list(scenario_list),
                        [baseline_index],
                        ["cropland", "grassland", "forest", "wetland", "total"],
                        [baseline],
                    ],
                    names=["scenario", "land_use", "year"],
                ),
            )

            emission_df.index.levels[0].astype(int)

            emission_df.loc[
                (
                    baseline_index,
                    "total",
                    baseline,
                ),
                "CH4",
            ] = lca.total_ch4_emission(
                land_use_data[base], land_use_data[base], transition_matrix[base], ef_country
            )
            emission_df.loc[
                (
                    baseline_index,
                    "total",
                    baseline,
                ),
                "CO2",
            ] = lca.total_co2_emission(
                land_use_data[base], land_use_data[base], transition_matrix[base], ef_country
            )

            emission_df.loc[
                (
                    baseline_index,
                    "total",
                    baseline,
                ),
                "N2O",
            ] = lca.total_n2o_emission(
                land_use_data[base], land_use_data[base], transition_matrix[base], ef_country
            )

            emission_df.loc[
                (baseline_index, "cropland", baseline),
                "CO2",
            ] = lca.total_co2_emission_cropland(
                land_use_data[base], land_use_data[base], transition_matrix[base], ef_country
            )

            emission_df.loc[
                (
                    baseline_index,
                    "cropland",
                    baseline,
                ),
                "CH4",
            ] = lca.total_ch4_emission_cropland(
                ef_country, transition_matrix[base], land_use_data[base], land_use_data[base]
            )

            emission_df.loc[
                (
                    baseline_index,
                    "cropland",
                    baseline,
                ),
                "N2O",
            ] = lca.total_n2o_emission_cropland(
                ef_country,
                transition_matrix[base],
                land_use_data[base],
                land_use_data[base],
            )

            emission_df.loc[
                (
                    baseline_index,
                    "grassland",
                    baseline,
                ),
                "CO2",
            ] = lca.total_co2_emission_grassland(
                land_use_data[base], land_use_data[base], transition_matrix[base], ef_country
            )

            emission_df.loc[
                (
                    baseline_index,
                    "grassland",
                    baseline,
                ),
                "CH4",
            ] = lca.total_ch4_emission_grassland(
                land_use_data[base], land_use_data[base], transition_matrix[base], ef_country
            )

            emission_df.loc[
                (baseline_index, "grassland", baseline),
                "N2O",
            ] = lca.total_n2o_emission_grassland(
                land_use_data[base], land_use_data[base], transition_matrix[base], ef_country
            )
            emission_df.loc[
                (
                    baseline_index,
                    "wetland",
                    baseline,
                ),
                "CO2",
            ] = lca.total_co2_emission_wetland(
                land_use_data[base],
                land_use_data[base],
                transition_matrix[base],
                ef_country,
            ) + lca.horticulture_co2_peat_export(
                ef_country, baseline, baseline
            )
            emission_df.loc[
                (
                    baseline_index,
                    "wetland",
                    baseline,
                ),
                "CH4",
            ] = lca.total_ch4_emission_wetland(
                land_use_data[base], land_use_data[base], transition_matrix[base], ef_country
            )
            emission_df.loc[
                (
                    baseline_index,
                    "wetland",
                    baseline,
                ),
                "N2O",
            ] = lca.total_n2o_emission_wetland(
                land_use_data[base],
                land_use_data[base],
                transition_matrix[base],
                ef_country,
            )
            emission_df.loc[
                (
                    baseline_index,
                    "forest",
                    baseline,
                ),
                "CO2",
            ] = lca.total_co2_emission_forest(
                land_use_data[base],
                land_use_data[base],
                transition_matrix[base],
                ef_country,
            )
            emission_df.loc[
                (baseline_index, "forest", baseline),
                "CH4",
            ] = lca.total_ch4_emission_forest(
                land_use_data[base], land_use_data[base], transition_matrix[base], ef_country
            )
            emission_df.loc[
                (baseline_index, "forest", baseline),
                "N2O",
            ] = lca.total_n2o_emission_forest(
                land_use_data[base], land_use_data[base], transition_matrix[base], ef_country
            )

            emission_df["CO2e"] = (
                emission_df["CO2"] + (emission_df["CH4"] * 28) + (emission_df["N2O"] * 295)
            )

            
            expected_file_name = "emission_df.csv"
            expected_file_path = os.path.join(tmp_dir, expected_file_name)

            #save results
            emission_df.to_csv(expected_file_path)

            
            # Check if the file was created as expected
            self.assertTrue(os.path.exists(expected_file_path), f"File {expected_file_name} was not created in temporary directory.")


# Running the tests
if __name__ == '__main__':
    unittest.main()

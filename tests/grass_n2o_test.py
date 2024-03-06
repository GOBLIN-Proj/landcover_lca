from landcover_lca.models import load_transition_matrix, load_land_use_data
import landcover_lca.lca_emission as lca
import pandas as pd
import os


def main():
    data_dir = "./data"

    ef_country = "ireland"
    baseline = 2020
    target = 2050

    transition = pd.read_csv(os.path.join(data_dir, "transition.csv"), index_col=0)
    land_uses = pd.read_csv(os.path.join(data_dir, "land_uses.csv"), index_col=0)

    transition_matrix = load_transition_matrix(transition, ef_country, baseline, target)

    land_use_data = load_land_use_data(land_uses, baseline)

    baseline_index = 0
    base = -baseline

    emission_df = pd.DataFrame(
        columns=["CO2", "CH4", "N2O", "CO2e"],
        index=pd.MultiIndex.from_product(
            [
                # list(scenario_list),
                [baseline_index],
                [ "grassland"],
                [baseline],
            ],
            names=["scenario", "land_use", "year"],
        ),
    )

    emission_df.index.levels[0].astype(int)

    
    emission_df.loc[
        (
            baseline_index,
            "grassland",
            baseline,
        ),
        "CO2",
    ] = lca.total_co2_emission_grassland(
        land_use_data[baseline_index], land_use_data[base], transition_matrix[baseline_index], ef_country
    )

    emission_df.loc[
        (
            baseline_index,
            "grassland",
            baseline,
        ),
        "CH4",
    ] = lca.total_ch4_emission_grassland(
        land_use_data[baseline_index], land_use_data[base], transition_matrix[baseline_index], ef_country
    )

    emission_df.loc[
        (baseline_index, "grassland", baseline),
        "N2O",
    ] = lca.total_n2o_emission_grassland(
        land_use_data[baseline_index], land_use_data[base], transition_matrix[baseline_index], ef_country
    )
   
    emission_df["CO2e"] = (
        emission_df["CO2"] + (emission_df["CH4"] * 28) + (emission_df["N2O"] * 295)
    )
    print(emission_df)


if __name__ == "__main__":
    main()

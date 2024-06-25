from landcover_lca.geo_goblin.geo_models import load_transition_matrix, load_land_use_data
import landcover_lca.geo_goblin.geo_lca_emissions as lca
import pandas as pd
import os


def main():
    data_dir = "./geo_data"

    ef_country = "ireland"
    baseline = 2020
    target = 2050

    transition = pd.read_csv(os.path.join(data_dir, "transition_matrix.csv"), index_col=0)
    land_uses = pd.read_csv(os.path.join(data_dir, "land_uses.csv"), index_col=0)

    transition_matrix = load_transition_matrix(transition, ef_country, baseline, target)

    land_use_data = load_land_use_data(land_uses, baseline)

    baseline_index = -1
    base = -baseline
    print(type(transition_matrix[base]))
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
        emission_df["CO2"] + (emission_df["CH4"] * 28) + (emission_df["N2O"] * 265)
    )
    print(emission_df)


if __name__ == "__main__":
    main()

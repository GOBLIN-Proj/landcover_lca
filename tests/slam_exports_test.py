
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
        columns=["N", "P", "PO4e"],
        index=pd.MultiIndex.from_product(
            [
                # list(scenario_list),
                [baseline_index],
                ["forest"],
                [baseline],
            ],
            names=["scenario", "land_use", "year"],
        ),
    )

    emission_df.index.levels[0].astype(int)

    emission_df.loc[
        (
            baseline_index,
            "forest",
            baseline,
        ),
        "N",
    ] = lca.exports_to_water_N_forest(
        land_use_data[base], land_use_data[base], transition_matrix[base], ef_country
    )

    emission_df.loc[
        (
            baseline_index,
            "forest",
            baseline,
        ),
        "P",
    ] = lca.exports_to_water_P_forest(
        land_use_data[base], land_use_data[base], transition_matrix[base], ef_country
    )

    emission_df.loc[
        (
            baseline_index,
            "forest",
            baseline,
        ),
        "PO4e",
    ] = lca.exports_to_water_PO4e_forest(
        land_use_data[base], land_use_data[base], transition_matrix[base], ef_country
    )


    print(emission_df)


    index = [int(i) for i in land_use_data.keys() if int(i) >= 0]

    sc_emission_df = pd.DataFrame(
        columns=["N", "P", "PO4e"],
        index=pd.MultiIndex.from_product(
            [
                list(index),
                ["forest"],
                [target],
            ],
            names=["scenario", "land_use", "year"],
        ),
    )
    sc_emission_df.index.levels[0].astype(int)

    for sc in index:
        sc_emission_df.loc[
        (
            sc,
            "forest",
            target,
        ),
            "N",
        ] = lca.exports_to_water_N_forest(
            land_use_data[sc], land_use_data[base], transition_matrix[sc], ef_country
        )

        sc_emission_df.loc[
        (
            sc,
            "forest",
            target,
        ),
            "P",
        ] = lca.exports_to_water_P_forest(
            land_use_data[sc], land_use_data[base], transition_matrix[sc], ef_country
        )


        sc_emission_df.loc[
        (
            sc,
            "forest",
            target,
        ),
            "PO4e",
        ] = lca.exports_to_water_PO4e_forest(
            land_use_data[sc], land_use_data[base], transition_matrix[sc], ef_country
        )

    print(sc_emission_df)

if __name__ == "__main__":
    main()

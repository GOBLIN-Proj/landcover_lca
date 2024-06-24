from landcover_lca.models import load_transition_matrix, load_land_use_data
import landcover_lca.lca_emission as lca
import pandas as pd
import os


def main():
    data_dir = "./goblin_lite_data"

    ef_country = "ireland"
    baseline = 2020
    target = 2050

    transition = pd.read_csv(os.path.join(data_dir, "transition_matrix.csv"), index_col=0)
    land_uses = pd.read_csv(os.path.join(data_dir, "landuse_data_test_version.csv"), index_col=0)

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
        emission_df["CO2"] + (emission_df["CH4"] * 28) + (emission_df["N2O"] * 265)
    )


    print(emission_df)


    
    index = [int(i) for i in land_use_data.keys() if int(i) >= 0]

    sc_emission_df = pd.DataFrame(
        columns=["CO2", "CH4", "N2O", "CO2e"],
        index=pd.MultiIndex.from_product(
            [
                list(index),
                ["cropland", "grassland", "forest", "wetland", "total"],
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
            "total",
            target,
        ),
            "CH4",
        ] = lca.total_ch4_emission(
            land_use_data[sc], land_use_data[base], transition_matrix[sc], ef_country
        )
        sc_emission_df.loc[
            (
                sc,
                "total",
                target,
            ),
            "CO2",
        ] = lca.total_co2_emission(
            land_use_data[sc], land_use_data[base], transition_matrix[sc], ef_country
        )

        sc_emission_df.loc[
            (
                sc,
                "total",
                target,
            ),
            "N2O",
        ] = lca.total_n2o_emission(
            land_use_data[sc], land_use_data[base], transition_matrix[sc], ef_country
        )

        sc_emission_df.loc[
            (sc, "cropland", target),
            "CO2",
        ] = lca.total_co2_emission_cropland(
            land_use_data[sc], land_use_data[base], transition_matrix[sc], ef_country
        )

        sc_emission_df.loc[
            (
                sc,
                "cropland",
                target,
            ),
            "CH4",
        ] = lca.total_ch4_emission_cropland(
            ef_country, transition_matrix[sc], land_use_data[base], land_use_data[sc]
        )

        sc_emission_df.loc[
            (
                sc,
                "cropland",
                target,
            ),
            "N2O",
        ] = lca.total_n2o_emission_cropland(
            ef_country,
            transition_matrix[sc],
            land_use_data[base],
            land_use_data[sc],
        )

        sc_emission_df.loc[
            (
                sc,
                "grassland",
                target,
            ),
            "CO2",
        ] = lca.total_co2_emission_grassland(
            land_use_data[sc], land_use_data[base], transition_matrix[sc], ef_country
        )

        sc_emission_df.loc[
            (
                sc,
                "grassland",
                target,
            ),
            "CH4",
        ] = lca.total_ch4_emission_grassland(
            land_use_data[sc], land_use_data[base], transition_matrix[sc], ef_country
        )

        sc_emission_df.loc[
            (sc, "grassland", target),
            "N2O",
        ] = lca.total_n2o_emission_grassland(
            land_use_data[sc], land_use_data[base], transition_matrix[sc], ef_country
        )
        sc_emission_df.loc[
            (
                sc,
                "wetland",
                target,
            ),
            "CO2",
        ] = lca.total_co2_emission_wetland(
            land_use_data[sc],
            land_use_data[base],
            transition_matrix[sc],
            ef_country,
        ) + lca.horticulture_co2_peat_export(
            ef_country, target, baseline
        )
        sc_emission_df.loc[
            (
                sc,
                "wetland",
                target,
            ),
            "CH4",
        ] = lca.total_ch4_emission_wetland(
            land_use_data[sc], land_use_data[base], transition_matrix[sc], ef_country
        )
        sc_emission_df.loc[
            (
                sc,
                "wetland",
                target,
            ),
            "N2O",
        ] = lca.total_n2o_emission_wetland(
            land_use_data[sc],
            land_use_data[base],
            transition_matrix[sc],
            ef_country,
        )
        sc_emission_df.loc[
            (
                sc,
                "forest",
                target,
            ),
            "CO2",
        ] = lca.total_co2_emission_forest(
            land_use_data[sc],
            land_use_data[base],
            transition_matrix[sc],
            ef_country,
        )
        sc_emission_df.loc[
            (sc, "forest", target),
            "CH4",
        ] = lca.total_ch4_emission_forest(
            land_use_data[sc], land_use_data[base], transition_matrix[sc], ef_country
        )
        sc_emission_df.loc[
            (sc, "forest", target),
            "N2O",
        ] = lca.total_n2o_emission_forest(
            land_use_data[sc], land_use_data[base], transition_matrix[sc], ef_country
        )

    sc_emission_df["CO2e"] = (
        sc_emission_df["CO2"] + (sc_emission_df["CH4"] * 28) + (sc_emission_df["N2O"] * 265)
    )

    print(sc_emission_df)

if __name__ == "__main__":
    main()

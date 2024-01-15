from landcover_lca.models import load_transition_matrix, load_land_use_data
import landcover_lca.lca_emission as landuse_lca
import pandas as pd
import os


def main():
    data_dir = "./data/goblin_lite_n/"

    ef_country = "ireland"
    baseline = 2020
    target = 2050

    transition = pd.read_csv(os.path.join(data_dir, "transition_matrix.csv"), index_col=0)
    land_uses = pd.read_csv(os.path.join(data_dir, "landuse_data.csv"), index_col=0)
    forest_data = pd.read_csv(os.path.join(data_dir, "forest_carbon_flux.csv"), index_col=0)

    transition_matrix = load_transition_matrix(transition, ef_country, baseline, target)

    land_use_data = load_land_use_data(land_uses, baseline)

    base = -baseline
    baseline = baseline
    target_year =target
    ef_country = ef_country
    land_use_data = land_use_data
    transition_matrix = transition_matrix
    forest_data = forest_data
    kg_to_kt = 1e-6
    t_to_kt = 1e-3

    index = [int(i) for i in land_use_data.keys() if int(i) >= 0]

    emission_df = pd.DataFrame(
        columns=["CO2", "CH4", "N2O", "CO2e"],
        index=pd.MultiIndex.from_product(
            [
                list(index),
                ["cropland", "grassland", "forest", "wetland", "total"],
                [target_year],
            ],
            names=["scenario", "land_use", "year"],
        ),
    )

    emission_df.index.levels[0].astype(int)

    for sc in index:
        future_forest_mask = (forest_data["Year"] == target_year) & (
            forest_data["Scenario"] == sc
        )

        emission_df.loc[
            (
                sc,
                "total",
                target_year,
            ),
            "CH4",
        ] = (
            landuse_lca.total_ch4_emission(
                land_use_data[sc],
                land_use_data[base],
                transition_matrix[sc],
                ef_country,
            )
            * kg_to_kt
        )
        emission_df.loc[
            (
                sc,
                "total",
                target_year,
            ),
            "CO2",
        ] = (
            (
                landuse_lca.total_co2_emission(
                    land_use_data[sc],
                    land_use_data[base],
                    transition_matrix[sc],
                    ef_country,
                )
                + landuse_lca.horticulture_co2_peat_export(
                    ef_country, target_year, baseline
                )
            )
            * kg_to_kt
        ) + (
            forest_data.loc[future_forest_mask, "Total Ecosystem"].item()
            * t_to_kt
            * 3.67
        )

        emission_df.loc[
            (
                sc,
                "total",
                target_year,
            ),
            "N2O",
        ] = (
            landuse_lca.total_n2o_emission(
                land_use_data[sc],
                land_use_data[base],
                transition_matrix[sc],
                ef_country,
            )
            * kg_to_kt
        )

        emission_df.loc[
            (sc, "cropland", target_year),
            "CO2",
        ] = (
            landuse_lca.total_co2_emission_cropland(
                land_use_data[sc],
                land_use_data[base],
                transition_matrix[sc],
                ef_country,
            )
            * kg_to_kt
        )

        emission_df.loc[
            (
                sc,
                "cropland",
                target_year,
            ),
            "CH4",
        ] = (
            landuse_lca.total_ch4_emission_cropland(
                ef_country,
                transition_matrix[sc],
                land_use_data[base],
                land_use_data[sc],
            )
            * kg_to_kt
        )

        emission_df.loc[
            (
                sc,
                "cropland",
                target_year,
            ),
            "N2O",
        ] = (
            landuse_lca.total_n2o_emission_cropland(
                ef_country,
                transition_matrix[sc],
                land_use_data[base],
                land_use_data[sc],
            )
            * kg_to_kt
        )

        emission_df.loc[
            (
                sc,
                "grassland",
                target_year,
            ),
            "CO2",
        ] = (
            landuse_lca.total_co2_emission_grassland(
                land_use_data[sc],
                land_use_data[base],
                transition_matrix[sc],
                ef_country,
            )
            * kg_to_kt
        )

        emission_df.loc[
            (
                sc,
                "grassland",
                target_year,
            ),
            "CH4",
        ] = (
            landuse_lca.total_ch4_emission_grassland(
                land_use_data[sc],
                land_use_data[base],
                transition_matrix[sc],
                ef_country,
            )
            * kg_to_kt
        )

        emission_df.loc[
            (sc, "grassland", target_year),
            "N2O",
        ] = (
            landuse_lca.total_n2o_emission_grassland(
                land_use_data[sc],
                land_use_data[base],
                transition_matrix[sc],
                ef_country,
            )
            * kg_to_kt
        )
        emission_df.loc[
            (
                sc,
                "wetland",
                target_year,
            ),
            "CO2",
        ] = (
            landuse_lca.total_co2_emission_wetland(
                land_use_data[sc],
                land_use_data[base],
                transition_matrix[sc],
                ef_country,
            )
            + landuse_lca.horticulture_co2_peat_export(
                ef_country, target_year, baseline
            )
        ) * kg_to_kt

        emission_df.loc[
            (
                sc,
                "wetland",
                target_year,
            ),
            "CH4",
        ] = (
            landuse_lca.total_ch4_emission_wetland(
                land_use_data[sc],
                land_use_data[base],
                transition_matrix[sc],
                ef_country,
            )
            * kg_to_kt
        )
        emission_df.loc[
            (
                sc,
                "wetland",
                target_year,
            ),
            "N2O",
        ] = (
            landuse_lca.total_n2o_emission_wetland(
                land_use_data[sc],
                land_use_data[base],
                transition_matrix[sc],
                ef_country,
            )
            * kg_to_kt
        )
        emission_df.loc[
            (
                sc,
                "forest",
                target_year,
            ),
            "CO2",
        ] = (
            landuse_lca.total_co2_emission_forest(
                land_use_data[sc],
                land_use_data[base],
                transition_matrix[sc],
                ef_country,
            )
            * kg_to_kt
        ) + (
            forest_data.loc[future_forest_mask, "Total Ecosystem"].item()
            * t_to_kt
            * 3.67
        )

        emission_df.loc[
            (sc, "forest", target_year),
            "CH4",
        ] = (
            landuse_lca.total_ch4_emission_forest(
                land_use_data[sc],
                land_use_data[base],
                transition_matrix[sc],
                ef_country,
            )
            * kg_to_kt
        )
        emission_df.loc[
            (sc, "forest", target_year),
            "N2O",
        ] = (
            landuse_lca.total_n2o_emission_forest(
                land_use_data[sc],
                land_use_data[base],
                transition_matrix[sc],
                ef_country,
            )
            * kg_to_kt
        )

    emission_df["CO2e"] = (
        emission_df["CO2"]
        + (emission_df["CH4"] * 28)
        + (emission_df["N2O"] * 295)
    )


    print(emission_df)


if __name__ == "__main__":
    main()

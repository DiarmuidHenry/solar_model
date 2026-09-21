from src.tariffs.ei_weekender_sunday_t import (
    get_import_price,
    get_export_price,
)


def calculate_costs(results):
    """
    Calculate electricity costs from simulation results.
    """

    results = results.copy()

    results["import_cost"] = (
        results.apply(
            lambda row:
                row["grid_import_kwh"]
                * get_import_price(row["timestamp"]),
            axis=1,
        )
    )

    results["export_revenue"] = (
        results["grid_export_kwh"]
        * get_export_price()
    )

    results["net_energy_cost"] = (
        results["import_cost"]
        - results["export_revenue"]
    )

    return results
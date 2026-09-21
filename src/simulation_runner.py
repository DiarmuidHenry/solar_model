import pandas as pd
from src.simulation import simulate_interval


def run_simulation(
    pv_file,
    usage_file,
    initial_battery_soc_kwh,
):
    # Load data

    pv = pd.read_csv(pv_file)
    usage = pd.read_csv(usage_file)

    # Convert timestamps

    pv["time"] = pd.to_datetime(pv["time"])

    usage["time"] = pd.to_datetime(
        usage["time"],
        format="%H:%M",
    ).dt.time

    # Match usage profile to each PV interval

    usage_lookup = (
        usage
        .set_index(["month", "weekday", "time"])
        ["expected_usage_kwh"]
        .to_dict()
    )

    results = []

    battery_soc_kwh = initial_battery_soc_kwh

    for _, row in pv.iterrows():

        # PVGIS gives hourly values
        hour_start = row["time"].floor("h")

        # Split hourly solar equally between two half-hours
        solar_kwh = (
            row["total_power_w"]
            / 1000
            * 0.5
        )

        for half_hour in [0, 30]:

            timestamp = (
                hour_start
                + pd.Timedelta(minutes=half_hour)
            )

            key = (
                timestamp.month,
                timestamp.weekday(),
                timestamp.time(),
            )

            if key not in usage_lookup:
                raise ValueError(
                    f"No usage profile found for {timestamp}"
                )

            load_kwh = usage_lookup[key]

            result = simulate_interval(
                timestamp=timestamp,
                solar_kwh=solar_kwh,
                load_kwh=load_kwh,
                battery_soc_kwh=battery_soc_kwh,
            )

            result["timestamp"] = timestamp
            result["solar_kwh"] = solar_kwh
            result["load_kwh"] = load_kwh

            results.append(result)

            battery_soc_kwh = result["battery_soc_kwh"]

    results = pd.DataFrame(results)

    return results
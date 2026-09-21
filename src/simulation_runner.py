import pandas as pd
from src.simulation import simulate_interval
from src.system import BATTERY_USABLE_CAPACITY_KWH


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

    pv["month"] = pv["time"].dt.month
    pv["weekday"] = pv["time"].dt.weekday
    pv["time_only"] = (
    pv["time"]
    .dt.floor("30min")
    .dt.time
    )

    results = []

    battery_soc_kwh = initial_battery_soc_kwh

    for _, row in pv.iterrows():

        usage_match = usage[
            (usage["month"] == row["month"])
            & (usage["weekday"] == row["weekday"])
            & (usage["time"] == row["time_only"])
        ]

        if usage_match.empty:
            raise ValueError(
                f"No usage profile found for {row['time']}"
            )

        load_kwh = usage_match.iloc[0][
            "expected_usage_kwh"
        ]

        result = simulate_interval(
            timestamp=row["time"],
            solar_kwh=row["total_generation_kwh"],
            load_kwh=load_kwh,
            battery_soc_kwh=battery_soc_kwh,
        )

        result["timestamp"] = row["time"]
        result["solar_kwh"] = row["total_generation_kwh"]
        result["load_kwh"] = load_kwh

        results.append(result)

        battery_soc_kwh = result["battery_soc_kwh"]

    results = pd.DataFrame(results)

    return results
import pandas as pd


def combine_arrays(east, west):
    combined = pd.DataFrame()
    combined["time"] = east["time"]
    combined["east_power_w"] = east["P"].round(3)
    combined["west_power_w"] = west["P"].round(3)
    combined["total_power_w"] = (
        combined["east_power_w"] + combined["west_power_w"]
    ).round(3)
    
    # Convert hourly power to energy
    combined["east_generation_kwh"] = (
        combined["east_power_w"] / 1000
    ).round(3)
    combined["west_generation_kwh"] = (
        combined["west_power_w"] / 1000
    ).round(3)
    combined["total_generation_kwh"] = (
        combined["total_power_w"] / 1000
    ).round(3)

    return combined


def analyse_generation(solar):
    # Copy df to avoid modifying original
    solar = solar.copy()
    solar["year"] = solar["time"].dt.year
    annual_generation = solar.groupby("year").agg(
        east_generation_kwh=("east_generation_kwh", "sum"),
        west_generation_kwh=("west_generation_kwh", "sum"),
        total_generation_kwh=("total_generation_kwh", "sum")
    )

    return annual_generation
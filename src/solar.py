import pandas as pd


def combine_arrays(east, west):
    combined = pd.DataFrame()
    combined["time"] = east["time"]
    combined["east_power_w"] = east["P"]
    combined["west_power_w"] = west["P"]
    combined["total_power_w"] = (
        combined["east_power_w"] + combined["west_power_w"]
    )
    
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
    solar["month"] = solar["time"].dt.month
    solar["month_name"] = solar["time"].dt.month_name()
    solar["date"] = solar["time"].dt.date
    
    # Annual generation
    annual_generation = solar.groupby("year").agg(
        east_generation_kwh=("east_generation_kwh", "sum"),
        west_generation_kwh=("west_generation_kwh", "sum"),
        total_generation_kwh=("total_generation_kwh", "sum")
    )
    
    # Monthly generation
    monthly_generation = solar.groupby(
        ["year", "month", "month_name"]
    ).agg(
        east_generation_kwh=("east_generation_kwh", "sum"),
        west_generation_kwh=("west_generation_kwh", "sum"),
        total_generation_kwh=("total_generation_kwh", "sum")
    )
    
    # Daily generation
    daily_generation = solar.groupby(
        "date"
    ).agg(
        east_generation_kwh=("east_generation_kwh", "sum"),
        west_generation_kwh=("west_generation_kwh", "sum"),
        total_generation_kwh=("total_generation_kwh", "sum")
    )
    

    return annual_generation, monthly_generation, daily_generation
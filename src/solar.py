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
    )
    combined["west_generation_kwh"] = (
        combined["west_power_w"] / 1000
    )
    combined["total_generation_kwh"] = (
        combined["total_power_w"] / 1000
    )
    
    # Round to remove floating point errors
    combined = combined.round(3)

    return combined
import pandas as pd


def combine_arrays(east, west):
    combined = pd.DataFrame()
    combined["time"] = east["time"]
    combined["east_power_w"] = east["P"]
    combined["west_power_w"] = west["P"]
    combined["total_power_w"] = (
        combined["east_power_w"] + combined["west_power_w"]
    )
    
    # Round to remove floating point errors
    combined = combined.round(3)

    return combined
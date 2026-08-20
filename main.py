from pathlib import Path
from src.pvgis import get_hourly_pv
from src.solar import (
    combine_arrays,
    analyse_generation,
    calculate_average_monthly_generation
)
from src.charts import (
    plot_monthly_generation,
    plot_daily_generation,
    plot_specific_day_generation
)
from datetime import date


# Property and roof details
LATITUDE = 54.208555
LONGITUDE = -8.515080
ROOF_TILT = 30    # degrees
EAST_FACING_PANELS = 9
WEST_FACING_PANELS = 13
PANEL_WATTAGE = 0.450    # kW

# East-facing panels
# Power in kW
EAST_POWER = EAST_FACING_PANELS * PANEL_WATTAGE
# East roof orientation (between +-180)
EAST_ASPECT = -78            

# West-facing panels
# Power in kW
WEST_POWER =  WEST_FACING_PANELS * PANEL_WATTAGE
# West roof orientation (between +-180)
WEST_ASPECT = 108


# Output folders
RAW_DATA_FOLDER = Path("data/raw")
RAW_DATA_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

# Donwload East data
east = get_hourly_pv(
    latitude=LATITUDE,
    longitude=LONGITUDE,
    peak_power=EAST_POWER,
    aspect=EAST_ASPECT,
    angle=ROOF_TILT,
)
east.to_csv(
    RAW_DATA_FOLDER / "east_hourly.csv",
    index=False
)

# Donwload West data
west = get_hourly_pv(
    latitude=LATITUDE,
    longitude=LONGITUDE,
    peak_power=WEST_POWER,
    aspect=WEST_ASPECT,
    angle=ROOF_TILT,
)
west.to_csv(
    RAW_DATA_FOLDER / "west_hourly.csv",
    index=False
)

# Combine East and West data
solar = combine_arrays(
    east,
    west
)
solar.to_csv(
    RAW_DATA_FOLDER / "combined_hourly.csv",
    index=False
)

# Analyse generation
annual_generation, monthly_generation, daily_generation = analyse_generation(solar)


# Average generation per month
average_monthly_generation = (
    calculate_average_monthly_generation(
        daily_generation,
        monthly_generation
    )
)

# # Plot monthly chart
# plot_monthly_generation(
#     monthly_generation
# )

# # Plot daily chart
# plot_daily_generation(
#     daily_generation
# )


# # Plot specific day chart. Example 01/07/23
# plot_specific_day_generation(
#     solar,
#     date(2020, 1, 1)
# )

# Print results
print("\nDownload complete!")

# print("\nEast data:")
# print(east.head())
# print("\nWest data:")
# print(west.head())

print("\nCombined data:")
print(solar.head())

# print("\nAnnual generation:")
# print(annual_generation.round(3))

# print("\nMonthly generation:")
# print(monthly_generation.round(3))

# print("\nDaily generation:")
# print(daily_generation.round(3))

print("\nAverage daily generation for each month:")
print(average_monthly_generation.round(3))
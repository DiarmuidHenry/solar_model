from pathlib import Path
from src.pvgis import get_hourly_pv

# Property and roof details

LATITUDE = 54.208555
LONGITUDE = -8.515080
ROOF_TILT = 30
EAST_FACING_PANELS = 9
WEST_FACING_PANELS = 13
PANEL_WATTAGE = 450

# East-facing panels
# Power in kW
EAST_POWER =  EAST_FACING_PANELS * PANEL_WATTAGE
# East roof orientation (between +-180)
EAST_ASPECT = -78            


# West-facing panels
# Power in kW
WEST_POWER =  WEST_FACING_PANELS * PANEL_WATTAGE
# West roof orientation (between +-180)
WEST_ASPECT = 102 

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

# Print results
print("\nDownload complete!")
print("\nEast data:")
print(east.head())
print("\nWest data:")
print(west.head())
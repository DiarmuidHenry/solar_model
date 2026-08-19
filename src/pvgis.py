import requests
import pandas as pd

PVGIS_URL = "https://re.jrc.ec.europa.eu/api/v5_3/seriescalc"


def get_hourly_pv(
    latitude,
    longitude,
    peak_power,
    aspect,
    angle=30,
    start_year=2020,
    end_year=2023,
):
    """
    Download hourly photovoltaic production data from PVGIS.

    Parameters
    ----------
    latitude : float
        Latitude of location

    longitude : float
        Longitude of  location

    peak_power : float
        Size of the solar array (kWp)

    aspect : float
        PVGIS panel azimuth

        0   = south
        -90 = east
        +90 = west

    angle : float
        Panel tilt in degrees

    start_year : int
        First year of hourly data

    end_year : int
        Final year of hourly data
    """

    params = {
        "lat": latitude,
        "lon": longitude,
        "outputformat": "json",
        "pvcalculation": 1,
        "peakpower": peak_power,
        "loss": 14,
        "angle": angle,
        "aspect": aspect,
        "startyear": start_year,
        "endyear": end_year,
        "raddatabase": "PVGIS-SARAH3",
    }

    print(f"Requesting PVGIS data for {peak_power:.3f} kWp...")

    response = requests.get(
        PVGIS_URL,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    hourly_data = data["outputs"]["hourly"]

    df = pd.DataFrame(hourly_data)

    df["time"] = pd.to_datetime(
        df["time"],
        format="%Y%m%d:%H%M",
    )

    return df
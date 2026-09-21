from datetime import datetime
from src.simulation import simulate_interval
from src.system import BATTERY_USABLE_CAPACITY_KWH


def test_solar_covers_house():
    result = simulate_interval(
        datetime(2026, 6, 1, 12, 0),
        solar_kwh=2.0,
        load_kwh=1.0,
        battery_soc_kwh=10.0,
    )

    assert result["solar_to_house_kwh"] == 1.0
    assert result["grid_import_kwh"] == 0.0
    assert result["grid_export_kwh"] == 1.0


def test_battery_covers_house():
    result = simulate_interval(
        datetime(2026, 6, 1, 12, 0),
        solar_kwh=0.0,
        load_kwh=2.0,
        battery_soc_kwh=10.0,
    )

    assert result["battery_to_house_kwh"] == 2.0
    assert result["grid_import_kwh"] == 0.0


def test_grid_covers_house_when_battery_empty():
    result = simulate_interval(
        datetime(2026, 6, 1, 12, 0),
        solar_kwh=0.0,
        load_kwh=2.0,   
        battery_soc_kwh=0.0,
    )

    assert result["grid_to_house_kwh"] == 2.0
    assert result["grid_import_kwh"] == 2.0


def test_inverter_limit():   
    result = simulate_interval(
        datetime(2026, 6, 1, 12, 0),
        solar_kwh=5.0,
        load_kwh=1.0,
        battery_soc_kwh=0.0,
    )

    total_inverter_output = (
        result["solar_to_house_kwh"]
        + result["solar_to_battery_kwh"]
        + result["solar_to_grid_kwh"]
    )

    assert total_inverter_output <= 2.5
    

def test_solar_and_battery_share_inverter_limit():
    result = simulate_interval(
        datetime(2026, 6, 1, 12, 0),
        solar_kwh=1.0,
        load_kwh=4.0,
        battery_soc_kwh=10.0,
    )

    total_inverter_output = (
        result["solar_to_house_kwh"]
        + result["battery_to_house_kwh"]
    )

    assert total_inverter_output == 2.5
    assert result["solar_to_house_kwh"] == 1.0
    assert result["battery_to_house_kwh"] == 1.5
    assert result["grid_import_kwh"] == 1.5


def test_solar_export_is_limited_by_inverter():
    result = simulate_interval(
        datetime(2026, 6, 1, 12, 0),
        solar_kwh=5.0,
        load_kwh=1.0,
        battery_soc_kwh=10.0,
    )

    assert result["solar_to_house_kwh"] == 1.0
    assert result["solar_to_grid_kwh"] == 1.5
    assert result["curtailed_solar_kwh"] == 2.5


def test_grid_import_can_exceed_inverter_limit():
    result = simulate_interval(
        datetime(2026, 6, 1, 12, 0),
        solar_kwh=0.0,
        load_kwh=6.0,
        battery_soc_kwh=0.0,
    )

    assert result["grid_to_house_kwh"] == 6.0
    assert result["grid_import_kwh"] == 6.0


def test_sunday_high_load_uses_grid():
    result = simulate_interval(
        datetime(2026, 6, 7, 12, 0),
        solar_kwh=0.0,
        load_kwh=6.0,
        battery_soc_kwh=18.432,
    )

    assert result["battery_to_house_kwh"] == 0.0
    assert result["grid_to_house_kwh"] == 6.0
    assert result["grid_import_kwh"] == 6.0
    

def test_simulation_runner():
    from src.simulation_runner import run_simulation

    results = run_simulation(
        "data/raw/combined_hourly.csv",
        "data/processed/expected_usage_profile.csv",
        initial_battery_soc_kwh=10.0,
    )

    assert len(results) > 0
    assert results["battery_soc_kwh"].min() >= 0
    assert (
        results["battery_soc_kwh"].max()
        <= BATTERY_USABLE_CAPACITY_KWH
    )
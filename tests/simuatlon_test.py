from datetime import datetime

from src.simulation import simulate_interval


def test_solar_covers_house():
    result = simulate_interval(
        datetime(2026, 6, 1, 12, 0),
        solar_kwh=2.0,
        load_kwh=1.0,
        battery_soc_kwh=10.0,
    )

    assert result["solar_to_house_kwh"] == 1.0
    assert result["grid_import_kwh"] == 0.0
    assert result["grid_export_kwh"] == 0.0


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
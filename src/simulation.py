from src.system import (
    BATTERY_USABLE_CAPACITY_KWH,
    BATTERY_MAX_CHARGE_KW,
    BATTERY_MAX_DISCHARGE_KW,
    BATTERY_ROUND_TRIP_EFFICIENCY,
    INVERTER_MAX_POWER_KW,
    INTERVAL_HOURS,
)

from src.strategies.ei_weekender_sunday_s import (
    choose_action,
    BATTERY_FULL_KWH,
    BATTERY_NORMAL_TARGET_KWH,
)


# Battery efficiency is split equally between charging
# and discharging.
BATTERY_CHARGE_EFFICIENCY = BATTERY_ROUND_TRIP_EFFICIENCY ** 0.5
BATTERY_DISCHARGE_EFFICIENCY = BATTERY_ROUND_TRIP_EFFICIENCY ** 0.5


def simulate_interval(
    timestamp,
    solar_kwh,
    load_kwh,
    battery_soc_kwh,
):
    """
    Simulate one half-hour interval.

    Inputs:
        timestamp          datetime
        solar_kwh          solar energy available during interval
        load_kwh           household energy demand
        battery_soc_kwh    battery state of charge at start

    Returns:
        Dictionary containing the actual energy flows
        and battery state of charge at the end.
    """

    # Basic checks

    if solar_kwh < 0:
        raise ValueError("solar_kwh cannot be negative")

    if load_kwh < 0:
        raise ValueError("load_kwh cannot be negative")

    if not 0 <= battery_soc_kwh <= BATTERY_USABLE_CAPACITY_KWH:
        raise ValueError("Invalid battery state of charge")

    # Get strategy decision

    action = choose_action(
        timestamp,
        solar_kwh,
        load_kwh,
        battery_soc_kwh,
    )

    # Initialise flows

    solar_to_house_kwh = 0.0
    solar_to_battery_kwh = 0.0
    solar_to_grid_kwh = 0.0

    grid_to_house_kwh = 0.0
    grid_to_battery_kwh = 0.0

    battery_to_house_kwh = 0.0

    curtailed_solar_kwh = 0.0

    battery_soc_end_kwh = battery_soc_kwh

    # Maximum energy that can pass through the battery during this interval.
    max_charge_energy = (
        BATTERY_MAX_CHARGE_KW
        * INTERVAL_HOURS
    )

    max_discharge_energy = (
        BATTERY_MAX_DISCHARGE_KW
        * INTERVAL_HOURS
    )

    # Maximum energy through the inverter
    max_inverter_energy = (
        INVERTER_MAX_POWER_KW
        * INTERVAL_HOURS
    )

    inverter_remaining_kwh = max_inverter_energy

    # Sunday free period
    is_sunday = timestamp.weekday() == 6

    is_free_period = (
        is_sunday
        and 8 <= timestamp.hour < 23
    )

    if is_free_period:

        # Solar supplies the house first
        solar_to_house_kwh = min(
            solar_kwh,
            load_kwh,
            inverter_remaining_kwh,
        )

        inverter_remaining_kwh -= solar_to_house_kwh

        solar_remaining = (
            solar_kwh
            - solar_to_house_kwh
        )

        load_remaining = (
            load_kwh
            - solar_to_house_kwh
        )

        # No battery discharging on Sunday

        # House deficit is supplied by the free grid.
        grid_to_house_kwh = load_remaining

        # If battery isn't full, charge it

        battery_room_kwh = (
            BATTERY_FULL_KWH
            - battery_soc_end_kwh
        )

        if battery_room_kwh > 0:
            # Maximum energy that can enter the battery
            # from solar during this interval.
            max_solar_charge = min(
                solar_remaining,
                max_charge_energy,
                battery_room_kwh / BATTERY_CHARGE_EFFICIENCY,
                inverter_remaining_kwh,
            )

            solar_to_battery_kwh = max_solar_charge

            inverter_remaining_kwh -= solar_to_battery_kwh

            battery_soc_end_kwh += (
                solar_to_battery_kwh
                * BATTERY_CHARGE_EFFICIENCY
            )

            solar_remaining -= solar_to_battery_kwh

            battery_room_kwh = (
                BATTERY_FULL_KWH
                - battery_soc_end_kwh
            )

            # Use free grid to finish charging
            if battery_room_kwh > 0:

                grid_charge_available = min(
                    max_charge_energy
                    - solar_to_battery_kwh,
                    battery_room_kwh
                    / BATTERY_CHARGE_EFFICIENCY,
                )

                if grid_charge_available > 0:

                    grid_to_battery_kwh = (
                        grid_charge_available
                    )

                    battery_soc_end_kwh += (
                        grid_to_battery_kwh
                        * BATTERY_CHARGE_EFFICIENCY
                    )

        # Export remaining inverter capacity
        solar_to_grid_kwh = min(
            solar_remaining,
            inverter_remaining_kwh,
        )

        solar_remaining -= solar_to_grid_kwh
        inverter_remaining_kwh -= solar_to_grid_kwh

        # Anything left is curtailed.
        curtailed_solar_kwh = solar_remaining

        return _finish_interval(
            action,
            battery_soc_end_kwh,
            solar_to_house_kwh,
            solar_to_battery_kwh,
            solar_to_grid_kwh,
            grid_to_house_kwh,
            grid_to_battery_kwh,
            battery_to_house_kwh,
            curtailed_solar_kwh,
        )

    ### Normal Operation
    # Solar supplies the house first.

    solar_to_house_kwh = min(
        solar_kwh,
        load_kwh,
        inverter_remaining_kwh,
    )

    inverter_remaining_kwh -= solar_to_house_kwh

    solar_remaining = (
        solar_kwh
        - solar_to_house_kwh
    )

    load_remaining = (
        load_kwh
        - solar_to_house_kwh
    )

    # House deficit
    if load_remaining > 0:

        if action == "battery_to_house":

            # Energy available from battery.
            battery_available_kwh = min(
                battery_soc_end_kwh,
                max_discharge_energy
                / BATTERY_DISCHARGE_EFFICIENCY,
            )

            battery_to_house_kwh = min(
                load_remaining,
                battery_available_kwh
                * BATTERY_DISCHARGE_EFFICIENCY,
                inverter_remaining_kwh,
            )

            inverter_remaining_kwh -= battery_to_house_kwh

            # Remove the corresponding stored energy.
            battery_soc_end_kwh -= (
                battery_to_house_kwh
                / BATTERY_DISCHARGE_EFFICIENCY
            )

            load_remaining -= battery_to_house_kwh

        # Anything still required comes from the grid.
        grid_to_house_kwh = load_remaining

    # Solar Surplus
    if solar_remaining > 0:

        if action == "solar_to_battery":

            battery_room_kwh = (
                BATTERY_NORMAL_TARGET_KWH
                - battery_soc_end_kwh
            )

            if battery_room_kwh > 0:

                solar_charge = min(
                    solar_remaining,
                    max_charge_energy,
                    battery_room_kwh
                    / BATTERY_CHARGE_EFFICIENCY,
                    inverter_remaining_kwh,
                )

                solar_to_battery_kwh = solar_charge

                inverter_remaining_kwh -= solar_charge

                battery_soc_end_kwh += (
                    solar_charge
                    * BATTERY_CHARGE_EFFICIENCY
                )

                solar_remaining -= solar_charge

        # Export remaining inverter capacity
        solar_to_grid_kwh = min(
            solar_remaining,
            inverter_remaining_kwh,
        )

        solar_remaining -= solar_to_grid_kwh
        inverter_remaining_kwh -= solar_to_grid_kwh

        # Anything left is curtailed.
        curtailed_solar_kwh = solar_remaining

    # Final validation
    return _finish_interval(
        action,
        battery_soc_end_kwh,
        solar_to_house_kwh,
        solar_to_battery_kwh,
        solar_to_grid_kwh,
        grid_to_house_kwh,
        grid_to_battery_kwh,
        battery_to_house_kwh,
        curtailed_solar_kwh,
    )


def _finish_interval(
    action,
    battery_soc_end_kwh,
    solar_to_house_kwh,
    solar_to_battery_kwh,
    solar_to_grid_kwh,
    grid_to_house_kwh,
    grid_to_battery_kwh,
    battery_to_house_kwh,
    curtailed_solar_kwh,
):
    """
    Finish an interval and validate the energy flows.
    """

    # Fix floating point error to keep battery capacity in range
    battery_soc_end_kwh = max(
        0.0,
        min(
            BATTERY_USABLE_CAPACITY_KWH,
            battery_soc_end_kwh,
        ),
    )

    grid_import_kwh = (
        grid_to_house_kwh
        + grid_to_battery_kwh
    )

    grid_export_kwh = solar_to_grid_kwh

    # Fundamental rule:
    # CANNOT import and export in the same interval.

    if (
        grid_import_kwh > 1e-9
        and grid_export_kwh > 1e-9
    ):
        raise RuntimeError(
            "Grid import and export occurred "
            "simultaneously."
        )

    return {
        "action": action,

        "solar_to_house_kwh": solar_to_house_kwh,
        "solar_to_battery_kwh": solar_to_battery_kwh,
        "solar_to_grid_kwh": solar_to_grid_kwh,

        "grid_to_house_kwh": grid_to_house_kwh,
        "grid_to_battery_kwh": grid_to_battery_kwh,

        "battery_to_house_kwh": battery_to_house_kwh,

        "grid_import_kwh": grid_import_kwh,
        "grid_export_kwh": grid_export_kwh,

        "curtailed_solar_kwh": curtailed_solar_kwh,

        "battery_soc_kwh": battery_soc_end_kwh,
    }
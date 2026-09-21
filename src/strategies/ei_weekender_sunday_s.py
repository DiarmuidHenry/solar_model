# Electric Ireland Weekender - Sunday strategy

SOLAR_TO_HOUSE = "solar_to_house"
SOLAR_TO_BATTERY = "solar_to_battery"
SOLAR_TO_GRID = "solar_to_grid"

GRID_TO_HOUSE = "grid_to_house"
GRID_TO_BATTERY = "grid_to_battery"

BATTERY_TO_HOUSE = "battery_to_house"

# Battery targets
BATTERY_FULL_KWH = 18.4
BATTERY_NORMAL_TARGET_KWH = 10.0


def choose_action(
    timestamp,
    solar_kwh,
    load_kwh,
    battery_soc_kwh,
):
    """
    Decide what the system should try to do during
    one half-hour period.
    The strategy decides the desired action.
    The simulation engine will later determine
    the actual energy flows and enforce physical
    limits.
    """

    is_sunday = timestamp.weekday() == 6

    # Sunday free-electricity period
    is_free_period = (
        is_sunday
        and 8 <= timestamp.hour < 23
    )

    if is_free_period:

        # Do not discharge the battery during the
        # free-electricity period.
        #
        # The goal is to have the battery completely
        # full by 22:00.

        if timestamp.hour < 22:

            if battery_soc_kwh < BATTERY_FULL_KWH:
                return "CHARGE_BATTERY"

            return "EXPORT_SURPLUS"

        # 22:00-23:00
        #
        # Battery should already be full.
        # Do not discharge it.

        return "EXPORT_SURPLUS"

    ### Outside free period

    # Solar cannot cover the house.
    if solar_kwh < load_kwh:

        if battery_soc_kwh > 0:
            return BATTERY_TO_HOUSE

        return GRID_TO_HOUSE

    # Solar exactly covers the house.
    if solar_kwh == load_kwh:
        return SOLAR_TO_HOUSE

    # Solar exceeds household demand.
    #
    # Charge the battery until it reaches the normal
    # 10 kWh target.
    if battery_soc_kwh < BATTERY_NORMAL_TARGET_KWH:
        return SOLAR_TO_BATTERY

    # Battery is at or above 10 kWh.
    # Export all remaining solar.
    return SOLAR_TO_GRID


SOLAR_TO_HOUSE = "solar_to_house"
SOLAR_TO_BATTERY = "solar_to_battery"
SOLAR_TO_GRID = "solar_to_grid"
GRID_TO_HOUSE = "grid_to_house"
GRID_TO_BATTERY = "grid_to_battery"
BATTERY_TO_HOUSE = "battery_to_house"


def choose_action(timestamp, solar_kwh, load_kwh, battery_soc_kwh):
    """
    Decide what the energy system should try to do
    during a single half-hour period.

    The strategy decides the desired energy flows.
    The simulation engine will later enforce:
    - 5 kW charge/discharge limits
    - battery capacity
    - battery efficiency
    - inverter limits
    """

    is_sunday = timestamp.weekday() == 6
    is_free_period = (
        is_sunday
        and 8 <= timestamp.hour < 23
    )

    # --------------------------------------------------
    # Sunday 08:00-23:00
    # --------------------------------------------------

    if is_free_period:

        # During the free period, the house can use
        # free electricity from the grid.
        #
        # Priority is to get the battery to 18.4 kWh
        # by 23:00.
        
        if battery_soc_kwh < 18.4:
            return "CHARGE_BATTERY"

        # Once the battery is full, surplus solar
        # can be exported.
        return "EXPORT_SURPLUS"

    # --------------------------------------------------
    # Outside Sunday 08:00-23:00
    # --------------------------------------------------

    if solar_kwh > load_kwh:

        # Solar can cover the house and leave a surplus.
        return "CHARGE_OR_EXPORT"

    elif solar_kwh < load_kwh:

        # Solar cannot cover the house.
        # Use the battery before importing from the grid.
        if battery_soc_kwh > 0:
            return "BATTERY_TO_HOUSE"

        return "GRID_TO_HOUSE"

    else:

        # Solar exactly matches household demand.
        return "SOLAR_TO_HOUSE"
    

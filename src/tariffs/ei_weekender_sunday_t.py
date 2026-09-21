from datetime import datetime

"""
Electric Ireland Weekender Sunday tariff
Prices in €/kWh
VAT 9%, Discount 16% applied where relevant
"""
DISCOUNT = 0.16
VAT = 0.09

IMPORT_PRICE = round(0.3752*(1+VAT)*(1-DISCOUNT),4)
SUNDAY_FREE_PRICE = 0.0000
EXPORT_PRICE = 0.1950
STANDING_CHARGE_ANNUAL = 230
PSO_ANNUAL = 19.10*(1+VAT)


def get_import_price(timestamp):
    """
    Return lectricity import price for a given datetime
    """

    # Sunday free period
    if timestamp.weekday() == 6:

        # 08:00 to 23:00 is free
        if 8 <= timestamp.hour < 23:
            return SUNDAY_FREE_PRICE

    # All other times
    return IMPORT_PRICE


def get_export_price():
    """
    Return electricity export price for a given datetime
    """

    return EXPORT_PRICE
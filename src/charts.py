import matplotlib.pyplot as plt


def plot_monthly_generation(monthly_generation):
    monthly_generation["total_generation_kwh"].plot(
        kind="bar"
    )
    plt.xlabel("Month")
    plt.ylabel("Generation (kWh)")
    plt.title("Monthly Solar Generation")
    plt.show()
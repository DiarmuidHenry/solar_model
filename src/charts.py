import matplotlib.pyplot as plt
import plotly.graph_objects as go


def plot_monthly_generation(monthly_generation):
    monthly_generation["total_generation_kwh"].plot(
        kind="bar"
    )
    plt.xlabel("Month")
    plt.ylabel("Generation (kWh)")
    plt.title("Monthly Solar Generation")
    plt.show()
    

def plot_daily_generation(daily_generation):
    daily_generation["total_generation_kwh"].plot(
        kind="bar"
    )
    plt.xlabel("Date")
    plt.ylabel("Generation (kWh)")
    plt.title("Daily Solar Generation")
    plt.show()


def plot_specific_day_generation(solar, date):
    selected_day = solar[
        solar["time"].dt.date == date
    ]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=selected_day["time"],
            y=selected_day["east_generation_kwh"],
            mode="lines",
            name="East"
        )
    )
    fig.add_trace(
        go.Scatter(
            x=selected_day["time"],
            y=selected_day["west_generation_kwh"],
            mode="lines",
            name="West"
        )
    )
    fig.add_trace(
        go.Scatter(
            x=selected_day["time"],
            y=selected_day["total_generation_kwh"],
            mode="lines",
            name="Total"
        )
    )
    fig.update_layout(
        title=f"Solar Generation - {date}",
        xaxis_title="Time",
        yaxis_title="Generation (kWh)"
    )

    fig.show()
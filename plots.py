import matplotlib.pyplot as plt
import pandas as pd


def draw_plot(data: dict):
    x_values = data.keys()
    y_values = data.values()
    plt.plot(x_values, y_values)
    plt.title("Distribution of delays")
    plt.xlabel("Delay in sec")
    plt.ylabel("No. of vehicles")
    plt.show()


def draw_quantile_plot(data: dict):
    delays_list = [delay for delay, count in data.items() for _ in range(count)]
    df = pd.DataFrame({"delay": delays_list})
    df["group"] = pd.qcut(
        df.index.values,
        q=8,
        labels=["0-12,5", "12,5-25", "25-37,5", "37,5-50", "50-62,5", "62,5-75", "75-87,5", "87,5-100"],
    )
    fig, ax = plt.subplots()
    xlabel = df["group"].unique()
    ylabel = df.groupby("group")["delay"].median()
    ax.bar(xlabel, ylabel)
    plt.title("Average delays in each group %")

    plt.show()

import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("AAPL.csv")
data["Date"] = pd.to_datetime(data["Date"])
data = data.set_index("Date")

cols = ["Open", "High", "Low", "Close", "Volume"]
data[cols] = data[cols].apply(pd.to_numeric, errors="coerce")

n = 100
data["Momentum"] = data["Close"] - data["Close"].shift(n)

data["Signal"] = 0
data.loc[data["Momentum"] > 0, "Signal"] = 1
data.loc[data["Momentum"] < 0, "Signal"] = -1

data["Position_Change"] = data["Signal"].diff()

fig, (ax1, ax2) = plt.subplots(
    2, 1,
    figsize=(18, 6),
    sharex=True,
    gridspec_kw={'height_ratios': [3, 1]}
)

ax1.plot(data.index, data["Close"], label="Close Price", color="blue", alpha=0.7)

ax1.scatter(
    data.index[data["Position_Change"] == 2],
    data["Close"][data["Position_Change"] == 2],
    label="Buy Signal (Momentum > 0)",
    marker="^",
    color="green",
    s=100,
)

ax1.scatter(
    data.index[data["Position_Change"] == -2],
    data["Close"][data["Position_Change"] == -2],
    label="Sell Signal (Momentum < 0)",
    marker="v",
    color="red",
    s=100,
)

ax1.set_title("Momentum-Based Trading Strategy")
ax1.set_ylabel("Price")
ax1.legend(loc="upper left")
ax1.grid(True)

ax2.plot(data.index, data["Momentum"], label=f"Momentum ({n})", color="purple")
ax2.axhline(0, color="black", linestyle="--", linewidth=1)
ax2.set_ylabel("Momentum")
ax2.set_xlabel("Date")
ax2.legend(loc="upper left")
ax2.grid(True)

plt.tight_layout()
plt.show()
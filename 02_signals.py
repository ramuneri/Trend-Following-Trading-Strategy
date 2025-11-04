import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("AAPL.csv")
data["Date"] = pd.to_datetime(data["Date"])
data = data.set_index("Date")

cols = ["Open", "High", "Low", "Close", "Volume"]
data[cols] = data[cols].apply(pd.to_numeric, errors="coerce")

data["Typical_Price"] = (data["High"] + data["Low"] + data["Close"]) / 3

n = 50
data["Momentum"] = data["Typical_Price"] - data["Typical_Price"].shift(n)

data["Signal"] = 0
data.loc[data["Momentum"] > 0, "Signal"] = 1
data.loc[data["Momentum"] < 0, "Signal"] = -1


fig, (ax1, ax2) = plt.subplots(
    2, 1,
    figsize=(18, 6),
    sharex=True,
    gridspec_kw={'height_ratios': [3, 1]}
)

ax1.scatter(
    data.index[data["Signal"].diff() == 2],
    data["Typical_Price"][data["Signal"].diff() == 2],
    label="Buy Signal (Momentum > 0)",
    marker="^",
    color="green",
)

ax1.scatter(
    data.index[data["Signal"].diff() == -2],
    data["Typical_Price"][data["Signal"].diff() == -2],
    label="Sell Signal (Momentum < 0)",
    marker="v",
    color="red",
)

ax1.plot(data.index, data["Typical_Price"], label="Typical Price", color="blue")
ax1.set_title("Momentum-Based Trading Strategy")
ax1.set_ylabel("Typical Price")
ax1.legend()
ax1.grid(True)

ax2.plot(data.index, data["Momentum"], label=f"Momentum ({n})", color="purple")
ax2.axhline(0, color="black", linestyle="--", linewidth=1)
ax2.set_ylabel("Momentum Indicator")
ax2.set_xlabel("Date")
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.show()

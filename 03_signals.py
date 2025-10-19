import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("AAPL.csv", parse_dates=["Date"])
data.set_index("Date", inplace=True)

cols = ["Open", "High", "Low", "Close", "Volume"]
data[cols] = data[cols].apply(pd.to_numeric, errors='coerce')

short_window = 20
long_window = 50

data["SMA_short"] = data["Close"].rolling(window=short_window).mean()
data["SMA_long"] = data["Close"].rolling(window=long_window).mean()

# Generate buy/sell signals
# 0 = no position, 1 = buy, -1 = sell
data["Signal"] = 0
data.loc[data["SMA_short"] > data["SMA_long"], "Signal"] = 1
data.loc[data["SMA_short"] < data["SMA_long"], "Signal"] = -1

# Crossover points (where signal changes)
data["Position_Change"] = data["Signal"].diff()

plt.figure(figsize=(16, 7))
plt.plot(data.index, data["Close"], label="Close Price", color="blue")
plt.plot(data.index, data["SMA_short"], label=f"SMA {short_window}", color="green")
plt.plot(data.index, data["SMA_long"], label=f"SMA {long_window}", color="red")

plt.scatter(
    data.index[data["Position_Change"] == 2],
    data["Close"][data["Position_Change"] == 2],
    label="Buy Signal",
    marker="^",
    color="green",
    s=100,
)

plt.scatter(
    data.index[data["Position_Change"] == -2],
    data["Close"][data["Position_Change"] == -2],
    label="Sell Signal",
    marker="v",
    color="red",
    s=100,
)

plt.title("Trend Following Signals (MA Crossover)")
plt.xlabel("Date")
plt.ylabel("Price (USD)")
plt.legend()
plt.grid(True)
plt.show()

# Optional: print a few signals
print(data[["Close", "SMA_short", "SMA_long", "Signal", "Position_Change"]].tail(10))

# Plot a stock’s close price with SMA(30) and SMA(200) lines.
# Mark buy/sell signals.
# Create a second plot showing how the portfolio value (1 share) changes over time when following those signals.
# Optimization to find which SMA periods (e.g. short vs. long) give the best performance.

# Close, SMAs and Signals
# -----------------------------------

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import yfinance as yf


def count_sma(data, w1, w2):
  data["SMA1"] = data["Close"].rolling(window=w1).mean()
  data["SMA2"] = data["Close"].rolling(window=w2).mean()
  return data

def count_signals(data):
  data["Signal"] = 0
  data.loc[data["SMA1"] > data["SMA2"], "Signal"] = 1
  data.loc[data["SMA1"] < data["SMA2"], "Signal"] = -1
  return data

def count_profit(data):
  data["Daily_change"] = data["Close"].diff() * data["Signal"].shift(1)
  data["All_profit"] = data["Daily_change"].cumsum()
  return data


ticker = "AAPL"
start = "2015-01-01"
end = "2025-01-01"
w1 = 30
w2 = 200

data = yf.download(ticker, start=start, end=end, interval="1d", auto_adjust=True)
data.columns = (col[0] for col in data.columns)

data = count_sma(data, w1, w2)
data = count_signals(data)

plt.figure(figsize=(18,7))
plt.plot(data.index, data["Close"], label="Price", color="blue")
plt.plot(data.index, data["SMA1"], label=f"SMA{w1}", color="orange")
plt.plot(data.index, data["SMA2"], label=f"SMA{w2}", color="yellow")

plt.scatter(
    data.index[data["Signal"].diff() == 2],
    data["Close"][data["Signal"].diff() == 2],
    label="Buy",
    marker="^",
    color="green"
)

plt.scatter(
    data.index[data["Signal"].diff() == -2],
    data["Close"][data["Signal"].diff() == -2],
    label="Sell",
    marker="v",
    color="red"
)
plt.title("Price, SMAs and Buy/Sell Signals")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Profit graph
# -----------------------------------

data = count_profit(data)

plt.figure(figsize=(18,7))
plt.plot(data.index, data["All_profit"], label="Profit", color="green")
plt.title("Profit")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()


# With optimized profit 
# -----------------------------------

best_w1 = 0
best_w2 = 0
best_profit = -99999

for w1 in range (10, 101, 10):
  for w2 in range (100, 251, 25):

    df = data.copy()
    df = count_sma(df, w1, w2)
    df = count_signals(df)
    df = count_profit(df)

    final_profit = df["All_profit"].iloc[-1]

    if final_profit > best_profit:
      best_profit = final_profit
      best_w1 = w1
      best_w2 = w2


data = count_profit(data)

data_op = data.copy()
data_op = count_sma(data_op, best_w1, best_w2)
data_op = count_signals(data_op)
data_op = count_profit(data_op)

plt.figure(figsize=(18,7))
plt.plot(data.index, data["All_profit"], label="Profit", color="green")
plt.plot(data_op.index, data_op["All_profit"], label="Profit Optimized", color="orange")
plt.title("Profits")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()


# TP/SL
# -----------------------------------

take_profit_pct = 0.05
stop_loss_pct = 0.03

data["Reason"] = ""
holding = False
entry_price = 0

for i in range(1, len(data)):
    price = data["Close"].iloc[i]
    signal_now = data["Signal"].iloc[i]
    signal_prev = data["Signal"].iloc[i - 1]

    if signal_now == 1 and signal_prev <= 0 and not holding:
        holding = True
        entry_price = price

    elif holding:
        change = (price - entry_price) / entry_price
        if change >= take_profit_pct:
            holding = False
            data.loc[data.index[i], "Reason"] = "Take"

        elif change <= -stop_loss_pct:
            holding = False
            data.loc[data.index[i], "Reason"] = "Stop"

plt.figure(figsize=(18, 7))
plt.plot(data.index, data["Close"], label="Close Price", color="blue")

plt.scatter(
    data.index[data["Reason"] == "Take"],
    data["Close"].loc[data["Reason"] == "Take"],
    label="Take Profit",
    color="lime",
    marker="*",
    s=150
)

plt.scatter(
    data.index[data["Reason"] == "Stop"],
    data["Close"].loc[data["Reason"] == "Stop"],
    label="Stop Loss",
    color="orange",
    marker="x",
    s=100
)

plt.title("Close Price with Take Profit and Stop Loss Markers")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()



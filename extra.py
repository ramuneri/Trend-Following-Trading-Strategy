# Plot a stock’s close price with SMA(30) and SMA(200) lines.
# Mark buy/sell signals.
# Create a second plot showing how the portfolio value (1 share) changes over time when following those signals.
# Optimization to find which SMA periods (e.g. short vs. long) give the best performance.

import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

ticker = "AAPL"
start = "2015-01-01"
end = "2025-01-01"
w1 = 30
w2 = 200


data = yf.download(ticker, start=start, end=end, interval="1d", auto_adjust=True)
data.columns = (col[0] for col in data.columns)

data["SMA30"] = data["Close"].rolling(window=w1).mean()
data["SMA200"] = data["Close"].rolling(window=w2).mean()

plt.figure(figsize=(16, 6))
plt.plot(data.index, data["Close"], label="Price", color="blue")
plt.plot(data.index, data["SMA30"], label="SMA30", color="orange")
plt.plot(data.index, data["SMA200"], label="SMA200", color="yellow")

data["Signal"] = 0
data.loc[data["SMA30"] > data["SMA200"], "Signal"] = 1
data.loc[data["SMA30"] < data["SMA200"], "Signal"] = -1

plt.scatter (
    data.index[data["Signal"].diff() == 2],
    data["Close"][data["Signal"].diff() == 2],
    label = "Buy signal",
    marker = "^",
    color = "green"
)

plt.scatter (
    data.index[data["Signal"].diff() == -2],
    data["Close"][data["Signal"].diff() == -2],
    label = "Sell signal",
    marker = "v",
    color = "red"
)


plt.title("Price and Averages")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.tight_layout()
plt.show()

# --------------------------------

data["Daily_return"] = data["Close"].pct_change()
data["Return"] = data["Daily_return"] * data["Signal"].shift(1)
data["All_profit"] = data["Return"].cumsum()

plt.figure(figsize=(16, 6))
plt.plot(data.index, data["All_profit"], label="Profit (1 Share)", color="green")
plt.title("Profit (%)")
plt.xlabel("Date")
plt.ylabel("Cumulative Profit (%)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# --------------------------------

data["Daily_change"] = data["Close"].diff()
data["Profit"] = data["Daily_change"] * data["Signal"].shift(1)
data["All_profit"] = data["Profit"].cumsum() 

plt.figure(figsize=(16, 6))
plt.plot(data.index, data["All_profit"], label="Profit (1 Share)", color="green")
plt.title("Profit (dolars)")
plt.xlabel("Date")
plt.ylabel("Cumulative Profit (dolars)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# --------------------------------

# Optimization
best_profit = -999999
best_w1 = 0
best_w2 = 0
results = []

for w1 in range(10, 101, 10):
    for w2 in range(100, 251, 25):
        if w1 >= w2:
            continue

        df = data.copy()
        df["SMA_short"] = df["Close"].rolling(window=w1).mean()
        df["SMA_long"] = df["Close"].rolling(window=w2).mean()

        df["Signal"] = 0
        df.loc[df["SMA_short"] > df["SMA_long"], "Signal"] = 1
        df.loc[df["SMA_short"] < df["SMA_long"], "Signal"] = -1

        df["Daily_change"] = df["Close"].diff()
        df["Profit"] = df["Daily_change"] * df["Signal"].shift(1)
        df["Cumulative_Profit"] = df["Profit"].cumsum()

        final_profit = df["Cumulative_Profit"].iloc[-1]
        results.append((w1, w2, final_profit))

        if final_profit > best_profit:
            best_profit = final_profit
            best_w1 = w1
            best_w2 = w2


print("Optimization results ($):")
for w1, w2, profit in results:
    print(f"SMA({w1}, {w2}) - Profit: ${profit}")

print(f"\nBest combination: SMA({best_w1}, {best_w2}) - Profit: ${best_profit}")

# Default
df_default = data.copy()
df_default["SMA_short"] = df_default["Close"].rolling(window=w1).mean()
df_default["SMA_long"] = df_default["Close"].rolling(window=w2).mean()

df_default["Signal"] = 0
df_default.loc[df_default["SMA_short"] > df_default["SMA_long"], "Signal"] = 1
df_default.loc[df_default["SMA_short"] < df_default["SMA_long"], "Signal"] = -1

df_default["Daily_change"] = df_default["Close"].diff()
df_default["Profit"] = df_default["Daily_change"] * df_default["Signal"].shift(1)
df_default["Profit"] = df_default["Profit"].cumsum()

# Optimized
df_best = data.copy()
df_best["SMA_short"] = df_best["Close"].rolling(window=best_w1).mean()
df_best["SMA_long"] = df_best["Close"].rolling(window=best_w2).mean()

df_best["Signal"] = 0
df_best.loc[df_best["SMA_short"] > df_best["SMA_long"], "Signal"] = 1
df_best.loc[df_best["SMA_short"] < df_best["SMA_long"], "Signal"] = -1

df_best["Daily_change"] = df_best["Close"].diff()
df_best["Profit"] = df_best["Daily_change"] * df_best["Signal"].shift(1)
df_best["Profit"] = df_best["Profit"].cumsum()


plt.figure(figsize=(16, 6))
plt.plot(df_default.index, df_default["Profit"], label=f"Default SMA({w1}, {w2})", color="orange")
plt.plot(df_best.index, df_best["Profit"], label=f"Optimized SMA({best_w1}, {best_w2})", color="green")
plt.title("Profit Over Time")
plt.xlabel("Date")
plt.ylabel("Profit ($)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()






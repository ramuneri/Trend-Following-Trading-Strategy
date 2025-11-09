import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def run_momentum_strategy(data, n):
    df = data.copy()
    df["Momentum"] = df["Typical_Price"] - df["Typical_Price"].shift(n)

    df["Signal"] = 0
    df.loc[df["Momentum"] > 0, "Signal"] = 1
    df.loc[df["Momentum"] < 0, "Signal"] = -1

    df["Daily_profit"] = df["Typical_Price"].diff() * df["Signal"].shift(1)
    df["All_profit"] = df["Daily_profit"].cumsum()

    return df


data = pd.read_csv("AAPL.csv")
data["Date"] = pd.to_datetime(data["Date"])
data = data.set_index("Date")

cols = ["Open", "High", "Low", "Close", "Volume"]
data[cols] = data[cols].apply(pd.to_numeric, errors="coerce")

data["Typical_Price"] = (data["High"] + data["Low"] + data["Close"]) / 3

n = 50
best_profit = -999999
best_n = 0
results = []

for n in range(5, 101, 5):
    df = run_momentum_strategy(data, n)
    total_profit = df["All_profit"].iloc[-1]
    results.append((n, total_profit))

    if total_profit > best_profit:
        best_profit = total_profit
        best_n = n

print("Momentum Optimization Results:")
for n, profit in results:
    print(f"n={n} - Profit: ${profit:,.2f}")
print(f"\nBest Momentum period n = {best_n}, Profit = ${best_profit:,.2f}")

df_default = run_momentum_strategy(data, n)
df_best = run_momentum_strategy(data, best_n)


fig, (ax1, ax2) = plt.subplots(
    2, 1, 
    figsize=(16, 8), 
    sharex=True,
    gridspec_kw={'height_ratios': [2, 1]}
)

ax1.plot(data.index, data["Typical_Price"], color="blue", label="Typical Price")
ax1.set_title("Momentum Strategy — Price and Profit (1 Share)")
ax1.set_ylabel("Price")
ax1.legend()
ax1.grid(True)

ax2.plot(df_default.index, df_default["All_profit"], label=f"Default n={n}", color="orange")
ax2.plot(df_best.index, df_best["All_profit"], label=f"Optimized n={best_n}", color="green")
ax2.axhline(0, color="black", linewidth=1)
ax2.set_ylabel("Profit per share")
ax2.set_xlabel("Date")
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.show()

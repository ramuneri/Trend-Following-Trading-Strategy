import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def sharpe_ratio(profit_series):
    returns = profit_series.diff().dropna()
    if returns.std() == 0 or np.isnan(returns.std()):
        return 0
    return (returns.mean() / returns.std()) * np.sqrt(252)


def run_momentum_strategy(data, n, commission):
    df = data.copy()
    df["Momentum"] = df["Typical_Price"] - df["Typical_Price"].shift(n)

    df["Signal"] = 0
    df.loc[df["Momentum"] > 0, "Signal"] = 1
    df.loc[df["Momentum"] < 0, "Signal"] = -1

    df["Daily_change"] = df["Typical_Price"].diff()

    df["Trade_cost"] = 0.0
    df.loc[df["Signal"].diff() != 0, "Trade_cost"] = df["Typical_Price"] * commission

    df["Daily_profit"] = (df["Daily_change"] * df["Signal"].shift(1)) - df["Trade_cost"]
    df["All_profit"] = df["Daily_profit"].cumsum()

    return df


data = pd.read_csv("AAPL.csv")
data["Date"] = pd.to_datetime(data["Date"])
data = data.set_index("Date")

cols = ["Open", "High", "Low", "Close", "Volume"]
data[cols] = data[cols].apply(pd.to_numeric, errors="coerce")

data["Typical_Price"] = (data["High"] + data["Low"] + data["Close"]) / 3


best_profit = -999999
best_sharpe = -999
best_n = 0
commission = 0.001
results = []

for n in range(5, 101, 5):
    df = run_momentum_strategy(data, n, commission)
    total_profit = df["All_profit"].iloc[-1]
    sharpe_val = sharpe_ratio(df["All_profit"])
    results.append((n, total_profit, sharpe_val))

    if sharpe_val > best_sharpe:
        best_sharpe = sharpe_val
        best_n = n


print("Momentum Optimization Results:")
for n, profit, sharpe_val in results:
    print(f"n={n:<3} - Profit: {profit:>10,.2f}$, Sharpe: {sharpe_val:>6.3f}")

print(f"\nBest Momentum period n = {best_n}, Sharpe = {best_sharpe:.3f}")


df_default = run_momentum_strategy(data, n, commission)
df_best = run_momentum_strategy(data, best_n, commission)


fig, (ax1, ax2) = plt.subplots(
    2, 1,
    figsize=(16, 8),
    sharex=True,
    gridspec_kw={'height_ratios': [2, 1]}
)

ax1.plot(data.index, data["Typical_Price"], color="blue", label="Typical Price")
ax1.set_title("Momentum Strategy")
ax1.set_ylabel("Price")
ax1.legend()
ax1.grid(True)

ax2.plot(df_default.index, df_default["All_profit"], label=f"Default n={n} (Sharpe: {sharpe_ratio(df_default['All_profit']):.3f})", color="orange")
ax2.plot(df_best.index, df_best["All_profit"], label=f"Optimized n={best_n} (Sharpe: {best_sharpe:.3f})", color="green")
ax2.axhline(0, color="black", linewidth=1)
ax2.set_ylabel("Profit per share")
ax2.set_xlabel("Date")
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.show()

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("AAPL.csv")
data["Date"] = pd.to_datetime(data["Date"])
data = data.set_index("Date")

cols = ["Open", "High", "Low", "Close", "Volume"]
data[cols] = data[cols].apply(pd.to_numeric, errors='coerce')

take_profit_pct = 0.05
stop_loss_pct = 0.03
commission = 0.001
initial_capital = 10_000
default_n = 50


def run_strategy(data, n, take_profit_pct=take_profit_pct, stop_loss_pct=stop_loss_pct, commission=commission):
    df = data.copy()
    df["Momentum"] = df["Close"] - df["Close"].shift(n)

    df["Signal"] = 0
    df.loc[df["Momentum"] > 0, "Signal"] = 1
    df.loc[df["Momentum"] < 0, "Signal"] = -1

    cash = initial_capital
    num_shares = 0
    buy_price = 0
    df["Reason"] = ""
    portfolio_values = []

    for i in range(1, len(df)):
        price = df["Close"].iloc[i]
        signal_now = df["Signal"].iloc[i]
        signal_prev = df["Signal"].iloc[i - 1]

        if signal_now == 1 and signal_prev <= 0 and cash > 0:
            num_shares = (cash * (1 - commission)) / price
            buy_price = price
            cash = 0

        elif signal_now == -1 and signal_prev >= 0 and num_shares > 0:
            cash = num_shares * price * (1 - commission)
            num_shares = 0
            buy_price = 0

        elif num_shares > 0:
            change = (price - buy_price) / buy_price
            if change >= take_profit_pct:
                cash = num_shares * price * (1 - commission)
                num_shares = 0
                buy_price = 0
                df.loc[df.index[i], "Reason"] = "Take Profit"
            elif change <= -stop_loss_pct:
                cash = num_shares * price * (1 - commission)
                num_shares = 0
                buy_price = 0
                df.loc[df.index[i], "Reason"] = "Stop Loss"

        portfolio_value = cash + num_shares * price
        portfolio_values.append(portfolio_value)

    df = df.iloc[1:]
    df["Portfolio_Value"] = portfolio_values
    return df

def sharpe_ratio(portfolio_values):
    returns = pd.Series(portfolio_values).pct_change().dropna()
    if returns.std() == 0:
        return 0
    return (returns.mean() / returns.std()) * np.sqrt(252)

best_sharpe = -999
best_n = 0
results = []

for n in range(5, 101, 5):
    df_temp = run_strategy(data, n)
    sharpe = sharpe_ratio(df_temp["Portfolio_Value"])
    final_value = df_temp["Portfolio_Value"].iloc[-1]
    profit = final_value - initial_capital

    results.append((n, sharpe, profit))
    if sharpe > best_sharpe:
        best_sharpe = sharpe
        best_n = n

print("Momentum Optimization Results:")
for n, sharpe, profit in results:
    print(f"Momentum({n}) → Sharpe: {sharpe:.3f}, Profit: ${profit:,.2f}")

print("\nBest Parameters:")
print(f"Best Momentum period n = {best_n}, Best Sharpe = {best_sharpe:.3f}")

df_default = run_strategy(data, default_n)
df_optimized = run_strategy(data, best_n)

fig, (ax1, ax2) = plt.subplots(
    2, 1,
    figsize=(18, 7),
    sharex=True,
    gridspec_kw={'height_ratios': [3, 1]}
)

ax1.plot(df_optimized.index, df_optimized["Close"], label="Close Price", color="blue")
ax1.scatter(
    df_optimized.index[df_optimized["Signal"].diff() == 2],
    df_optimized["Close"][df_optimized["Signal"].diff() == 2],
    label="Buy Signal", marker="^", color="green", s=100
)
ax1.scatter(
    df_optimized.index[df_optimized["Signal"].diff() == -2],
    df_optimized["Close"][df_optimized["Signal"].diff() == -2],
    label="Sell Signal", marker="v", color="red", s=100
)

tp_idx = df_optimized.index[df_optimized["Reason"] == "Take Profit"]
sl_idx = df_optimized.index[df_optimized["Reason"] == "Stop Loss"]
ax1.scatter(tp_idx, df_optimized["Close"].loc[tp_idx], color="lime", marker="*", s=150, label="Take Profit")
ax1.scatter(sl_idx, df_optimized["Close"].loc[sl_idx], color="orange", marker="x", s=100, label="Stop Loss")

ax1.set_title("Momentum Strategy with Price and Trade Signals")
ax1.set_ylabel("Price ($)")
ax1.legend()
ax1.grid(True)

ax2.plot(df_optimized.index, df_optimized["Momentum"], label=f"Momentum ({best_n})", color="purple")
ax2.axhline(0, color="gray", linestyle="--", linewidth=1)
ax2.set_title("Momentum Indicator")
ax2.set_xlabel("Date")
ax2.set_ylabel("Momentum")
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.show()

plt.figure(figsize=(16, 6))
plt.plot(df_default.index, df_default["Portfolio_Value"], label=f"Default Momentum({default_n})", color="orange")
plt.plot(df_optimized.index, df_optimized["Portfolio_Value"], label=f"Optimized Momentum({best_n})", color="green")
plt.title("Momentum Strategy Portfolio Value Comparison")
plt.xlabel("Date")
plt.ylabel("Portfolio Value ($)")
plt.legend()
plt.grid()
plt.show()

final_value_opt = df_optimized["Portfolio_Value"].iloc[-1]
profit_opt = final_value_opt - initial_capital
final_value_def = df_default["Portfolio_Value"].iloc[-1]
profit_def = final_value_def - initial_capital

print(f"Default Momentum({default_n}): Final portfolio = ${final_value_def:,.2f}, Profit = ${profit_def:,.2f}")
print(f"Optimized Momentum({best_n}): Final portfolio = ${final_value_opt:,.2f}, Profit = ${profit_opt:,.2f}")

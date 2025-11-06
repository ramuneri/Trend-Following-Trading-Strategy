import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("AAPL.csv")
data["Date"] = pd.to_datetime(data["Date"])
data = data.set_index("Date")

cols = ["Open", "High", "Low", "Close", "Volume"]
data[cols] = data[cols].apply(pd.to_numeric, errors="coerce")

data["Typical_Price"] = (data["High"] + data["Low"] + data["Close"]) / 3


def run_strategy(data, n, take_profit_pct, stop_loss_pct, commission, initial_capital):
    df = data.copy()
    df["Momentum"] = df["Typical_Price"] - df["Typical_Price"].shift(n)
    df["Signal"] = 0
    df.loc[df["Momentum"] > 0, "Signal"] = 1
    df.loc[df["Momentum"] < 0, "Signal"] = -1

    cash = initial_capital
    num_shares = 0
    buy_price = 0
    portfolio_values = []
    df["Reason"] = ""

    for i in range(1, len(df)):
        price = df["Typical_Price"].iloc[i]
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


def sharpe(portfolio_values):
    returns = pd.Series(portfolio_values).pct_change().dropna()
    if returns.std() == 0:
        return 0
    return (returns.mean() / returns.std()) * np.sqrt(252)


initial_capital = 10_000
take_profit_pct = 0.05
stop_loss_pct = 0.03
commission = 0.001
default_n = 50


df = run_strategy(data, default_n, take_profit_pct, stop_loss_pct, commission, initial_capital)

fig, (ax1, ax2) = plt.subplots(
    2, 1,
    figsize=(18, 7),
    sharex=True,
    gridspec_kw={'height_ratios': [3, 1]}
)

ax1.plot(df.index, df["Typical_Price"], label="Typical Price", color="blue", alpha=0.7)

ax1.scatter(
    df.index[df["Signal"].diff() == 2],
    df["Typical_Price"][df["Signal"].diff() == 2],
    label="Buy Signal",
    color="green",
    marker="^"
)

ax1.scatter(df.index[df["Signal"].diff() == -2],
            df["Typical_Price"][df["Signal"].diff() == -2],
            label="Sell Signal",
            color="red",
            marker="v"
)

tp_idx = df.index[df["Reason"] == "Take Profit"]
sl_idx = df.index[df["Reason"] == "Stop Loss"]

ax1.scatter(tp_idx, df["Typical_Price"].loc[tp_idx], color="lime", marker="*", s=150, label="Take Profit")
ax1.scatter(sl_idx, df["Typical_Price"].loc[sl_idx], color="orange", marker="x", s=100, label="Stop Loss")

ax1.set_title("Momentum Strategy (Typical Price) — Buy/Sell/TP/SL")
ax1.set_ylabel("Typical Price")
ax1.legend()
ax1.grid(True)

ax2.plot(df.index, df["Momentum"], label=f"Momentum ({default_n})", color="purple")
ax2.axhline(0, color="gray", linestyle="--", linewidth=1)
ax2.set_title("Momentum Indicator")
ax2.set_xlabel("Date")
ax2.set_ylabel("Momentum")
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.show()


best_sharpe = -999
best_n = default_n
results = []

for n in range(5, 101, 5):
    df_opt = run_strategy(data, n, take_profit_pct, stop_loss_pct, commission, initial_capital)
    sharpe_value = sharpe(df_opt["Portfolio_Value"])
    final_value = df_opt["Portfolio_Value"].iloc[-1]
    profit = final_value - initial_capital
    results.append((n, sharpe_value, profit))
    if sharpe_value > best_sharpe:
        best_sharpe = sharpe_value
        best_n = n

print("\nMomentum Optimization Results:")
for n, sharpe_value, profit in results:
    print(f"Momentum({n}) → Sharpe: {sharpe_value:.3f}, Profit: ${profit:,.2f}")

print(f"\nBest n = {best_n}, Best Sharpe = {best_sharpe:.3f}")


df_default = run_strategy(data, default_n, take_profit_pct, stop_loss_pct, commission, initial_capital)
df_optimized = run_strategy(data, best_n, take_profit_pct, stop_loss_pct, commission, initial_capital)

plt.figure(figsize=(16, 7))

plt.plot(df_optimized.index, df_optimized["Portfolio_Value"], label=f"Optimized Momentum({best_n}) - Sharpe: {best_sharpe:.3f}", color="green")
plt.plot(df_default.index, df_default["Portfolio_Value"], label=f"Default Momentum({n}) - Sharpe: {sharpe(df_default['Portfolio_Value']):.3f}", color="orange")
plt.title("Portfolio Value Comparison")
plt.xlabel("Date")
plt.ylabel("Portfolio Value")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()


final_default = df_default["Portfolio_Value"].iloc[-1]
final_optimized = df_optimized["Portfolio_Value"].iloc[-1]

profit_default = final_default - initial_capital
profit_optimized = final_optimized - initial_capital

print(f"\nDefault (n={default_n}) Final: ${final_default:,.2f} Profit: ${profit_default:,.2f} ({profit_default/initial_capital*100:.2f}%)")
print(f"Optimized (n={best_n}) Final: ${final_optimized:,.2f} Profit: ${profit_optimized:,.2f} ({profit_optimized/initial_capital*100:.2f}%)")

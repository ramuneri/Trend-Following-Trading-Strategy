import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf


def run_strategy(data, window, take_profit_pct, stop_loss_pct, commission, initial_capital):
    df = data.copy()

    df["SMA"] = df["Typical_Price"].rolling(window=window).mean()

    df["Signal"] = 0
    df.loc[df["Typical_Price"] > df["SMA"], "Signal"] = 1
    df.loc[df["Typical_Price"] < df["SMA"], "Signal"] = -1

    cash = initial_capital
    shares = 0
    buy_price = 0
    portfolio_values = []
    df["Reason"] = ""

    for i in range(1, len(df)):
        price = df["Typical_Price"].iloc[i]
        signal_now = df["Signal"].iloc[i]
        signal_prev = df["Signal"].iloc[i - 1]

        # Buy signal (price crosses above SMA)
        if signal_now == 1 and signal_prev <= 0 and cash > 0:
            shares = (cash * (1 - commission)) / price
            buy_price = price
            cash = 0

        # Sell signal (price crosses below SMA)
        elif signal_now == -1 and signal_prev >= 0 and shares > 0:
            cash = shares * price * (1 - commission)
            shares = 0
            buy_price = 0

        # Check take profit / stop loss while holding
        elif shares > 0:
            change = (price - buy_price) / buy_price
            if change >= take_profit_pct:
                cash = shares * price * (1 - commission)
                shares = 0
                buy_price = 0
                df.loc[df.index[i], "Reason"] = "Take Profit"
            elif change <= -stop_loss_pct:
                cash = shares * price * (1 - commission)
                shares = 0
                buy_price = 0
                df.loc[df.index[i], "Reason"] = "Stop Loss"

        portfolio_value = cash + shares * price
        portfolio_values.append(portfolio_value)

    df = df.iloc[1:]
    df["Portfolio_Value"] = portfolio_values
    return df


def sharpe_ratio(portfolio_values):
    returns = pd.Series(portfolio_values).pct_change().dropna()
    if returns.std() == 0:
        return 0
    return (returns.mean() / returns.std()) * np.sqrt(252)



ticker = "AAPL"
start = "2020-01-01"
end = "2025-01-01"
window = 50

take_profit_pct = 0.05
stop_loss_pct = 0.03
commission = 0.001
initial_capital = 10_000

data = yf.download(ticker, start=start, end=end, interval="1d", auto_adjust=True)
# data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]
data.columns = [col[0] for col in data.columns]

data["Typical_Price"] = (data["High"] + data["Low"] + data["Close"]) / 3
# data.dropna(inplace=True)
data["SMA"] = data["Typical_Price"].rolling(window=window).mean()


data = run_strategy(data, window, take_profit_pct, stop_loss_pct, commission, initial_capital)

plt.figure(figsize=(16,7))
plt.plot(data.index, data["Typical_Price"], label="Price", color="blue")
plt.plot(data.index, data["SMA"], label="SMA", color="orange")

plt.scatter(data.index[data["Signal"].diff() == 2],
            data["Typical_Price"][data["Signal"].diff() == 2],
            marker="^",
            color="green",
            label="Buy Signal")
plt.scatter(data.index[data["Signal"].diff() == -2],
            data["Typical_Price"][data["Signal"].diff() == -2],
            marker="v",
            color="red",
            label="Sell Signal"
            )

tp_idx = data.index[data["Reason"] == "Take Profit"]
sl_idx = data.index[data["Reason"] == "Stop Loss"]

plt.scatter(tp_idx,
            data["Typical_Price"].loc[tp_idx],
            color="lime",
            marker="*",
            s=150,
            label="Take Profit"
            )

plt.scatter(sl_idx,
            data["Typical_Price"].loc[sl_idx],
            color="orange",
            marker="x",
            s=100,
            label="Stop Loss"\
            )

plt.title("Mini Strategy")
plt.xlabel("Date")
plt.ylabel("Price")
plt.grid(True)
plt.legend()
plt.show()


# ===============================
# 4️⃣ Parameter Optimization Loop
# ===============================
best_sharpe = -999
best_window = window
results = []

for window in range(5, 101, 5):
    df = run_strategy(data, window, take_profit_pct, stop_loss_pct, commission, initial_capital)
    sharpe = sharpe_ratio(df["Portfolio_Value"])
    final_value = df["Portfolio_Value"].iloc[-1]
    profit = final_value - initial_capital

    results.append((window, sharpe, profit))
    if sharpe > best_sharpe:
        best_sharpe = sharpe
        best_window = window

# Print optimization summary
print("SMA Optimization Results (using Typical Price):")
for window, sharpe, profit in results:
    print(f"SMA({window}) → Sharpe: {sharpe:.3f}, Profit: ${profit:,.2f}")

print("\nBest Parameters:")
print(f"Best SMA window = {best_window}, Best Sharpe = {best_sharpe:.3f}")


# ===============================
# 5️⃣ Run Best vs Default Strategy
# ===============================
df_optimized = run_strategy(data, best_window, take_profit_pct, stop_loss_pct, commission, initial_capital)
df_default = run_strategy(data, window, take_profit_pct, stop_loss_pct, commission, initial_capital)

# ===============================
# 6️⃣ Plot Portfolio Value Comparison
# ===============================
plt.figure(figsize=(16, 7))
plt.plot(df_optimized.index, df_optimized["Portfolio_Value"],
         label=f"Optimized SMA({best_window}) - Sharpe: {best_sharpe:.3f}", color="green")
plt.plot(df_default.index, df_default["Portfolio_Value"],
         label=f"Default SMA({window}) - Sharpe: {sharpe_ratio(df_default['Portfolio_Value']):.3f}", color="orange")

plt.title("Portfolio Value: Default vs Optimized SMA Strategy (Typical Price)")
plt.xlabel("Date")
plt.ylabel("Portfolio Value (USD)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()


# ===============================
# 8️⃣ Print Final Statistics
# ===============================
final_default = df_default["Portfolio_Value"].iloc[-1]
final_optimized = df_optimized["Portfolio_Value"].iloc[-1]

profit_default = final_default - initial_capital
profit_optimized = final_optimized - initial_capital

print(f"\nDefault SMA({window}) → Final Value: ${final_default:,.2f}, Profit: ${profit_default:,.2f} ({profit_default/initial_capital*100:.2f}%)")
print(f"Optimized SMA({best_window}) → Final Value: ${final_optimized:,.2f}, Profit: ${profit_optimized:,.2f} ({profit_optimized/initial_capital*100:.2f}%)")

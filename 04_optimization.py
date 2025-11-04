import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("AAPL.csv")
data["Date"] = pd.to_datetime(data["Date"])
data = data.set_index("Date")

cols = ["Open", "High", "Low", "Close", "Volume"]
data[cols] = data[cols].apply(pd.to_numeric, errors='coerce')

data["Typical_Price"] = (data["High"] + data["Low"] + data["Close"]) / 3

def run_strategy(data, n, take_profit_pct, stop_loss_pct, commission):
    df = data.copy()
    df["Momentum"] = df["Typical_Price"] - df["Typical_Price"].shift(n)

    df["Signal"] = 0
    df.loc[df["Momentum"] > 0, "Signal"] = 1
    df.loc[df["Momentum"] < 0, "Signal"] = -1

    cash = initial_capital
    num_shares = 0
    buy_price = 0
    portfolio_values = []

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
            if change >= take_profit_pct or change <= -stop_loss_pct:
                cash = num_shares * price * (1 - commission)
                num_shares = 0
                buy_price = 0

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


n = 50
initial_capital = 10_000
take_profit_pct = 0.05
stop_loss_pct = 0.03
commission = 0.001

best_sharpe = -999
best_n = 0
results = []

for n in range(5, 101, 5):
    df = run_strategy(data, n, take_profit_pct, stop_loss_pct, commission)
    sharpe = sharpe_ratio(df["Portfolio_Value"])
    final_value = df["Portfolio_Value"].iloc[-1]
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

df_optimized = run_strategy(data, best_n, take_profit_pct, stop_loss_pct, commission)
df_default = run_strategy(data, n, take_profit_pct, stop_loss_pct, commission)

plt.figure(figsize=(16, 7))
plt.plot(df_optimized.index, df_optimized["Portfolio_Value"], label=f"Optimized Momentum({best_n}) - Sharpe: {best_sharpe:.3f}", color="green")
plt.plot(df_default.index, df_default["Portfolio_Value"], label=f"Default Momentum({n}) - Sharpe: {sharpe_ratio(df_default['Portfolio_Value']):.3f}", color="orange")
plt.title("Momentum Strategy Portfolio Value")
plt.xlabel("Date")
plt.ylabel("Portfolio Value")
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()

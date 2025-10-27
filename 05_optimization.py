import numpy as np
import pandas as pd

data = pd.read_csv("AAPL.csv")
data["Date"] = pd.to_datetime(data["Date"])
data = data.set_index("Date")

cols = ["Open", "High", "Low", "Close", "Volume"]
data[cols] = data[cols].apply(pd.to_numeric, errors='coerce')

take_profit_pct = 0.05
stop_loss_pct = 0.03
commission = 0.001

def run_strategy(data, short_window, long_window, take_profit_pct=take_profit_pct, stop_loss_pct=stop_loss_pct, commission=commission):
    df = data.copy()
    
    df["SMA_short"] = df["Close"].rolling(window=short_window).mean()
    df["SMA_long"] = df["Close"].rolling(window=long_window).mean()
        
    df["Signal"] = 0
    df.loc[df["SMA_short"] > df["SMA_long"], "Signal"] = 1
    df.loc[df["SMA_short"] < df["SMA_long"], "Signal"] = -1

    cash = 10_000
    portfolio_values = []
    num_shares = 0
    buy_price = 0

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


best_sharpe = -999
best_params = (0, 0)
results = []

for short_window in range(10, 31, 5):
    for long_window in range(40, 101, 10):
        if short_window >= long_window:
            continue

        df = run_strategy(data, short_window, long_window)
        sharpe = sharpe_ratio(df["Portfolio_Value"])
        final_value = df["Portfolio_Value"].iloc[-1]
        profit = final_value - 10_000

        results.append((short_window, long_window, sharpe, profit))

        if sharpe > best_sharpe:
            best_sharpe = sharpe
            best_params = (short_window, long_window)


print("Optimization Results:")
for short, long, sharpe, profit in results:
    print(f"SMA({short}, {long}) → Sharpe: {sharpe:.3f}, Profit: ${profit:,.2f}")

print("\nBest Parameters:")
print(f"Short SMA = {best_params[0]}, Long SMA = {best_params[1]}, Best Sharpe = {best_sharpe:.3f}")


# atspausdinti pelno kitimo grafiką ir palyginti su neoptimizuotais parametrais (0.5 balo)

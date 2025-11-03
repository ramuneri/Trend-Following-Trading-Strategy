import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

ticker = "AAPL"
data = yf.download(ticker, start="2020-01-01", end="2025-01-01", interval="1d", auto_adjust=True)
data.columns = [col[0] for col in data.columns]

window = 50
data["SMA"] = data["Close"].rolling(window=window).mean()

data["Signal"] = 0
data.loc[data["Close"] > data["SMA"], "Signal"] = 1
data.loc[data["Close"] < data["SMA"], "Signal"] = -1

initial_capital = 10_000
cash = initial_capital
shares = 0
portfolio_values = []

for i in range(1, len(data)):
    price = data["Close"].iloc[i]
    signal_now = data["Signal"].iloc[i]
    signal_prev = data["Signal"].iloc[i - 1]

    if signal_now == 1 and signal_prev <= 0 and cash > 0:
        shares = cash / price
        cash = 0

    elif signal_now == -1 and signal_prev >= 0 and shares > 0:
        cash = shares * price
        shares = 0

    portfolio_value = cash + shares * price
    portfolio_values.append(portfolio_value)

data = data.iloc[1:]
data["Portfolio_Value"] = portfolio_values

plt.figure(figsize=(14, 6))
plt.plot(data.index, data["Close"], label="Close Price", color="blue")
plt.plot(data.index, data["SMA"], label=f"SMA {window}", color="orange")

plt.scatter(data.index[data["Signal"].diff() == 2],
            data["Close"][data["Signal"].diff() == 2],
            marker="^", color="green", s=100, label="Buy Signal")

plt.scatter(data.index[data["Signal"].diff() == -2],
            data["Close"][data["Signal"].diff() == -2],
            marker="v", color="red", s=100, label="Sell Signal")

plt.title("Mini Strategy: Single SMA Crossover")
plt.xlabel("Date")
plt.ylabel("Price (USD)")
plt.legend()
plt.grid(True)
plt.show()

final_value = data["Portfolio_Value"].iloc[-1]
profit = final_value - initial_capital
print(f"Initial capital: ${initial_capital:,.2f}")
print(f"Final portfolio value: ${final_value:,.2f}")
print(f"Total profit: ${profit:,.2f} ({profit/initial_capital*100:.2f}%)")

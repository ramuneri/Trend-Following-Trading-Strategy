import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("AAPL.csv", parse_dates=["Date"])
data.set_index("Date", inplace=True)
cols = ["Open", "High", "Low", "Close", "Volume"]
data[cols] = data[cols].apply(pd.to_numeric, errors='coerce')

short_window = 20
long_window = 50
data["SMA_short"] = data["Close"].rolling(window=short_window).mean()
data["SMA_long"] = data["Close"].rolling(window=long_window).mean()

data["Signal"] = 0
data.loc[data["SMA_short"] > data["SMA_long"], "Signal"] = 1
data.loc[data["SMA_short"] < data["SMA_long"], "Signal"] = -1

data["Position_Change"] = data["Signal"].diff()

plt.figure(figsize=(16, 7))
plt.plot(data.index, data["Close"], label="Close Price", color="blue", alpha=0.6)
plt.plot(data.index, data["SMA_short"], label=f"SMA {short_window}", color="green")
plt.plot(data.index, data["SMA_long"], label=f"SMA {long_window}", color="red")

plt.scatter(
    data.index[data["Position_Change"] == 2],
    data["Close"][data["Position_Change"] == 2],
    label="Buy Signal",
    marker="^",
    color="green",
    s=100,
)

plt.scatter(
    data.index[data["Position_Change"] == -2],
    data["Close"][data["Position_Change"] == -2],
    label="Sell Signal",
    marker="v",
    color="red",
    s=100,
)

plt.title("Trend Following: Moving Averages + Signals")
plt.xlabel("Date")
plt.ylabel("Price (USD)")
plt.legend()
plt.grid(True)
plt.show()


# Simulate
initial_capital = 10_000
position = 0 # shares currently held
cash = initial_capital
portfolio_values = []

for i in range(1, len(data)):
    price = data["Close"].iloc[i]

    # Buy if signal turns from -1/0 to 1
    if data["Signal"].iloc[i] == 1 and data["Signal"].iloc[i - 1] <= 0:
        position = cash / price

    # Sell if signal turns from 1 to -1
    elif data["Signal"].iloc[i] == -1 and data["Signal"].iloc[i - 1] >= 0:
        cash = position * price
        position = 0

    portfolio_value = cash + position * price
    portfolio_values.append(portfolio_value)

data = data.iloc[1:]  # remove the first row (since loop starts at 1)???
data["Portfolio_Value"] = portfolio_values

fig, ax1 = plt.subplots(figsize=(17, 7))

ax1.set_xlabel("Date")
ax1.set_ylabel("Close Price", color="blue")
ax1.plot(data.index, data["Close"], label="Close Price", color="blue")
ax1.plot(data.index, data["SMA_short"], label=f"SMA {short_window}", color="green", linewidth=1)
ax1.plot(data.index, data["SMA_long"], label=f"SMA {long_window}", color="red", linewidth=1)

ax1.scatter(
    data.index[data["Position_Change"] == 2],
    data["Close"][data["Position_Change"] == 2],
    label="Buy Signal",
    marker="^",
    color="green",
    s=100,
)
ax1.scatter(
    data.index[data["Position_Change"] == -2],
    data["Close"][data["Position_Change"] == -2],
    label="Sell Signal",
    marker="v",
    color="red",
    s=100,
)

ax1.tick_params(axis='y', labelcolor="blue")
ax1.grid(True)

ax2 = ax1.twinx()
ax2.set_ylabel("Portfolio Value", color="purple")
ax2.plot(data.index, data["Portfolio_Value"], label="Portfolio Value", color="purple", linewidth=3)
ax2.tick_params(axis='y', labelcolor="purple")

fig.suptitle("Trend Following Strategy")
ax1.legend(loc="upper left")
ax2.legend(loc="upper right")

fig.tight_layout()
plt.show()

final_value = data["Portfolio_Value"].iloc[-1]
profit = final_value - initial_capital
print(f"Initial capital: ${initial_capital:,.2f}")
print(f"Final portfolio value: ${final_value:,.2f}")
print(f"Total profit: ${profit:,.2f} ({profit/initial_capital*100:.2f}%)")

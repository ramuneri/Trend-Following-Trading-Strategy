import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("AAPL.csv")
data["Date"] = pd.to_datetime(data["Date"])

data = data.set_index("Date")

cols = ["Open", "High", "Low", "Close", "Volume"]
data[cols] = data[cols].apply(pd.to_numeric, errors='coerce')

short_window = 20
long_window = 50
data["SMA_short"] = data["Close"].rolling(window=short_window).mean()
data["SMA_long"] = data["Close"].rolling(window=long_window).mean()

plt.figure(figsize=(16, 7))
plt.plot(data.index, data["Close"], label="Close Price", color="blue", alpha=0.6)
plt.plot(data.index, data["SMA_short"], label=f"SMA {short_window}", color="green")
plt.plot(data.index, data["SMA_long"], label=f"SMA {long_window}", color="red")





data["Signal"] = 0
data.loc[data["SMA_short"] > data["SMA_long"], "Signal"] = 1
data.loc[data["SMA_short"] < data["SMA_long"], "Signal"] = -1

data["Position_Change"] = data["Signal"].diff()


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
plt.ylabel("Price")
plt.grid(True)
plt.legend()
plt.show()


# Simulate
initial_capital = 10_000
cash = initial_capital
portfolio_values = []
num_of_shares = 0
take_profit_pct = 0.05
stop_loss_pct = 0.03
commission = 0.001

data["Reason"] = ""

for i in range(1, len(data)):
    price = data["Close"].iloc[i]

    # buy   
    if data["Signal"].iloc[i] == 1 and data["Signal"].iloc[i - 1] <= 0 and cash > 0:
        num_of_shares = (cash * (1 - commission)) / price
        buy_price = price
        cash = 0

    # sell
    elif data["Signal"].iloc[i] == -1 and data["Signal"].iloc[i - 1] >= 0 and num_of_shares > 0:
        cash = num_of_shares * price * (1 - commission)
        num_of_shares = 0
        buy_price = 0

    elif num_of_shares > 0:
        change = (price - buy_price) / buy_price

        # take profit
        if change >= take_profit_pct:
            cash = num_of_shares * price * (1 - commission)
            num_of_shares = 0
            buy_price = 0
            data.loc[data.index[i], "Reason"] = "Take Profit"

        # stop loss
        elif change <= -stop_loss_pct:
            cash = num_of_shares * price * (1 - commission)
            num_of_shares = 0
            buy_price = 0
            data.loc[data.index[i], "Reason"] = "Stop Loss"

    portfolio_value = cash + num_of_shares * price
    portfolio_values.append(portfolio_value)

data = data.iloc[1:]
data["Portfolio_Value"] = portfolio_values

fig, ax1 = plt.subplots(figsize=(17, 7))

ax1.set_xlabel("Date")
ax1.set_ylabel("Close Price")
ax1.plot(data.index, data["Close"], label="Close Price", color="blue")
ax1.plot(data.index, data["SMA_short"], label=f"SMA {short_window}", color="green", linewidth=1)
ax1.plot(data.index, data["SMA_long"], label=f"SMA {long_window}", color="orange", linewidth=1)

# Take Profit and Stop Loss markers
tp_idx = data.index[data["Reason"] == "Take Profit"]
sl_idx = data.index[data["Reason"] == "Stop Loss"]

ax1.scatter(tp_idx, data["Close"].loc[tp_idx], color="lime", marker="*", s=150, label="Take Profit")
ax1.scatter(sl_idx, data["Close"].loc[sl_idx], color="red", marker="x", s=100, label="Stop Loss")


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

ax1.tick_params(axis='y')
ax1.grid(True)

ax2 = ax1.twinx()
ax2.set_ylabel("Portfolio Value")
ax2.plot(data.index, data["Portfolio_Value"], label="Portfolio Value", color="purple", linewidth=1)
ax2.tick_params(axis='y')

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

import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("AAPL.csv")
data["Date"] = pd.to_datetime(data["Date"])
data = data.set_index("Date")

cols = ["Open", "High", "Low", "Close", "Volume"]
data[cols] = data[cols].apply(pd.to_numeric, errors="coerce")

data["Typical_Price"] = (data["High"] + data["Low"] + data["Close"]) / 3

n = 50  # lookback period
data["Momentum"] = data["Typical_Price"] - data["Typical_Price"].shift(n)

data["Signal"] = 0
data.loc[data["Momentum"] > 0, "Signal"] = 1
data.loc[data["Momentum"] < 0, "Signal"] = -1

data["Position_Change"] = data["Signal"].diff()

initial_capital = 10_000
cash = initial_capital
num_of_shares = 0
take_profit_pct = 0.05
stop_loss_pct = 0.03
commission = 0.001

data["Reason"] = ""
portfolio_values = []

for i in range(1, len(data)):
    price = data["Typical_Price"].iloc[i]
    signal_now = data["Signal"].iloc[i]
    signal_prev = data["Signal"].iloc[i - 1]

    if signal_now == 1 and signal_prev <= 0 and cash > 0:
        num_of_shares = (cash * (1 - commission)) / price
        buy_price = price
        cash = 0

    elif signal_now == -1 and signal_prev >= 0 and num_of_shares > 0:
        cash = num_of_shares * price * (1 - commission)
        num_of_shares = 0
        buy_price = 0

    elif num_of_shares > 0:
        change = (price - buy_price) / buy_price
        if change >= take_profit_pct:
            cash = num_of_shares * price * (1 - commission)
            num_of_shares = 0
            buy_price = 0
            data.loc[data.index[i], "Reason"] = "Take Profit"
        elif change <= -stop_loss_pct:
            cash = num_of_shares * price * (1 - commission)
            num_of_shares = 0
            buy_price = 0
            data.loc[data.index[i], "Reason"] = "Stop Loss"

    portfolio_value = cash + num_of_shares * price
    portfolio_values.append(portfolio_value)

data = data.iloc[1:]
data["Portfolio_Value"] = portfolio_values

fig, (ax1, ax2) = plt.subplots(
    2, 1,
    figsize=(18, 6),
    sharex=True,
    gridspec_kw={'height_ratios': [3, 1]}
)

ax1.plot(data.index, data["Typical_Price"], label="Typical Price", color="blue", alpha=0.7)

ax1.scatter(
    data.index[data["Position_Change"] == 2],
    data["Typical_Price"][data["Position_Change"] == 2],
    label="Buy Signal",
    marker="^",
    color="green",
    s=100,
)

ax1.scatter(
    data.index[data["Position_Change"] == -2],
    data["Typical_Price"][data["Position_Change"] == -2],
    label="Sell Signal",
    marker="v",
    color="red",
    s=100,
)

tp_idx = data.index[data["Reason"] == "Take Profit"]
sl_idx = data.index[data["Reason"] == "Stop Loss"]
ax1.scatter(tp_idx, data["Typical_Price"].loc[tp_idx], color="lime", marker="*", s=150, label="Take Profit")
ax1.scatter(sl_idx, data["Typical_Price"].loc[sl_idx], color="orange", marker="x", s=100, label="Stop Loss")

ax1.set_title("Momentum Strategy (using Typical Price)")
ax1.set_ylabel("Typical Price")
ax1.legend()
ax1.grid(True)

ax2.plot(data.index, data["Momentum"], label=f"Momentum ({n})", color="purple")
ax2.axhline(0, color="gray", linestyle="--", linewidth=1)
ax2.set_title("Momentum Indicator")
ax2.set_xlabel("Date")
ax2.set_ylabel("Momentum")
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.show()

final_value = data["Portfolio_Value"].iloc[-1]
profit = final_value - initial_capital
print(f"Initial capital: ${initial_capital:,.2f}")
print(f"Final portfolio value: ${final_value:,.2f}")
print(f"Total profit: ${profit:,.2f} ({profit/initial_capital*100:.2f}%)")

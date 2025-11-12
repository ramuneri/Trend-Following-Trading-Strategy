import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("AAPL.csv")
data["Date"] = pd.to_datetime(data["Date"])
data = data.set_index("Date")

cols = ["Open", "High", "Low", "Close", "Volume"]
data[cols] = data[cols].apply(pd.to_numeric, errors="coerce")

data["Typical_Price"] = (data["High"] + data["Low"] + data["Close"]) / 3


n = 50
data["Momentum"] = data["Typical_Price"] - data["Typical_Price"].shift(n)

data["Signal"] = 0
data.loc[data["Momentum"] > 0, "Signal"] = 1
data.loc[data["Momentum"] < 0, "Signal"] = -1


take_profit_pct = 0.05
stop_loss_pct = 0.03
commission = 0.001

data["Reason"] = ""
profit_values = []
hold = False
entry_price = 0
cumulative_profit = 0

for i in range(1, len(data)):
    price = data["Typical_Price"].iloc[i]
    signal_now = data["Signal"].iloc[i]
    signal_prev = data["Signal"].iloc[i - 1]

    if signal_now == 1 and signal_prev <= 0 and not hold:
        hold = True
        entry_price = price
        data.loc[data.index[i], "Reason"] = "Buy"

    elif signal_now == -1 and signal_prev >= 0 and hold:
        cumulative_profit += (price - entry_price) * (1 - commission)
        hold = False
        entry_price = 0
        data.loc[data.index[i], "Reason"] = "Sell"

    elif hold:
        change = (price - entry_price) / entry_price
        if change >= take_profit_pct:
            cumulative_profit += (price - entry_price) * (1 - commission)
            hold = False
            entry_price = 0
            data.loc[data.index[i], "Reason"] = "Take Profit"
        elif change <= -stop_loss_pct:
            cumulative_profit += (price - entry_price) * (1 - commission)
            hold = False
            entry_price = 0
            data.loc[data.index[i], "Reason"] = "Stop Loss"

    profit_values.append(cumulative_profit)

data = data.iloc[1:]
data["Profit"] = profit_values

fig, (ax1, ax2) = plt.subplots(
    2, 1,
    figsize=(18, 7),
    sharex=True,
    gridspec_kw={'height_ratios': [3, 1]}
)

ax1.plot(data.index, data["Typical_Price"], label="Typical Price", color="blue", alpha=0.7)

ax1.scatter(
    data.index[data["Reason"] == "Buy"], 
    data["Typical_Price"].loc[data["Reason"] == "Buy"], 
    label="Buy Signal",
    color="green",
    marker="^",
    s=100
)

ax1.scatter(data.index[data["Reason"] == "Sell"], 
    data["Typical_Price"].loc[data["Reason"] == "Sell"], 
    label="Sell Signal",
    color="red",
    marker="v",
    s=100
)

ax1.scatter(
    data.index[data["Reason"] == "Take Profit"], 
    data["Typical_Price"].loc[data["Reason"] == "Take Profit"], 
    label="Take Profit",
    color="lime",
    marker="*",
    s=150
)

ax1.scatter(data.index[data["Reason"] == "Stop Loss"], 
    data["Typical_Price"].loc[data["Reason"] == "Stop Loss"], 
    label="Stop Loss",
    color="orange",
    marker="x",
    s=100
)

ax1.set_title("Momentum Strategy (1 Share) — Buy/Sell/TP/SL")
ax1.set_ylabel("Price")
ax1.legend()
ax1.grid(True)

ax2.plot(data.index, data["Momentum"], label=f"Momentum ({n})", color="purple")
ax2.axhline(0, color="gray", linestyle="--", linewidth=1)
ax2.set_xlabel("Date")
ax2.set_ylabel("Momentum")
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.show()

final_profit = data["Profit"].iloc[-1]
print(f"Profit per share: ${final_profit:,.2f}")

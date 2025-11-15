import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("AAPL.csv")
data["Date"] = pd.to_datetime(data["Date"])
data = data.set_index("Date")

cols = ["Open", "High", "Low", "Close", "Volume"]
data[cols] = data[cols].apply(pd.to_numeric, errors="coerce")



n = 50
take_profit_pct = 0.05
stop_loss_pct   = 0.03
commission      = 0.001
holding         = False
entry_price     = 0

data["Reason"] = ""
profits = []


data["Momentum"] = data["Close"] - data["Close"].shift(n)

data["Signal"] = 0
data.loc[data["Momentum"] > 0, "Signal"] = 1
data.loc[data["Momentum"] < 0, "Signal"] = -1

cumulative_profit = 0


for i in range(1, len(data)):
    prev_close = data["Close"].iloc[i - 1]
    curr_close = data["Close"].iloc[i]
    high = data["High"].iloc[i]
    low = data["Low"].iloc[i]

    signal_now = data["Signal"].iloc[i]
    signal_prev = data["Signal"].iloc[i - 1]

    if signal_now == 1 and signal_prev <= 0 and not holding:
        entry_price = (prev_close + curr_close) / 2
        entry_price *= (1 + commission)

        holding = True
        data.loc[data.index[i], "Reason"] = "Buy"

    elif signal_now == -1 and signal_prev >= 0 and holding:

        exit_price = (prev_close + curr_close) / 2
        exit_price *= (1 - commission)

        cumulative_profit += (exit_price - entry_price)
        holding = False
        entry_price = 0

        data.loc[data.index[i], "Reason"] = "Sell"

    elif holding:

        tp_price = entry_price * (1 + take_profit_pct)
        sl_price = entry_price * (1 - stop_loss_pct)

        if high >= tp_price:
            exit_price = tp_price * (1 - commission)
            cumulative_profit += (exit_price - entry_price)
            holding = False
            entry_price = 0
            data.loc[data.index[i], "Reason"] = "Take Profit"

        elif low <= sl_price:
            exit_price = sl_price * (1 - commission)
            cumulative_profit += (exit_price - entry_price)
            holding = False
            entry_price = 0
            data.loc[data.index[i], "Reason"] = "Stop Loss"

    profits.append(cumulative_profit)

data = data.iloc[1:]
data["Profit"] = profits



fig, (ax1, ax2) = plt.subplots(
    2, 1, figsize=(18, 8), sharex=True,
    gridspec_kw={'height_ratios': [3, 1]}
)

ax1.plot(data.index, data["Close"], label="Close Price", color="blue")

ax1.scatter(data.index[data["Reason"] == "Buy"],
            data["Close"].loc[data["Reason"] == "Buy"],
            marker="^", color="green", s=120, label="Buy")

ax1.scatter(data.index[data["Reason"] == "Sell"],
            data["Close"].loc[data["Reason"] == "Sell"],
            marker="v", color="red", s=120, label="Sell")

ax1.scatter(data.index[data["Reason"] == "Take Profit"],
            data["Close"].loc[data["Reason"] == "Take Profit"],
            marker="*", color="lime", s=160, label="Take Profit")

ax1.scatter(data.index[data["Reason"] == "Stop Loss"],
            data["Close"].loc[data["Reason"] == "Stop Loss"],
            marker="x", color="orange", s=100, label="Stop Loss")

ax1.set_title("Momentum Strategy with Realistic Execution (Crossing Logic)")
ax1.set_ylabel("Price")
ax1.grid(True)
ax1.legend()


ax2.plot(data.index, data["Momentum"], color="purple", label=f"Momentum ({n})")
ax2.axhline(0, color="black", linestyle="--")
ax2.set_ylabel("Momentum")
ax2.set_xlabel("Date")
ax2.grid(True)
ax2.legend()

plt.tight_layout()
plt.show()



diff_signal = data["Signal"].diff().fillna(0)
data["Trade_cost"] = 0.0
data.loc[diff_signal != 0, "Trade_cost"] = data["Close"] * commission

data["Daily_profit"] = data["Close"].diff().fillna(0) * data["Signal"].shift(1).fillna(0) - data["Trade_cost"]
data["All_profit"] = data["Daily_profit"].cumsum()

plt.figure(figsize=(16, 6))
plt.plot(data.index, data["All_profit"], color="green")
plt.title("Profit (1 Share)")
plt.xlabel("Date")
plt.ylabel("Profit ($)")
plt.grid(True)
plt.tight_layout()
plt.show()

print(f"\nFINAL PROFIT PER SHARE: ${data['All_profit'].iloc[-1]:,.2f}")

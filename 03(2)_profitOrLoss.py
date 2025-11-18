import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("AAPL.csv")
data["Date"] = pd.to_datetime(data["Date"])
data = data.set_index("Date")

cols = ["Open", "High", "Low", "Close", "Volume"]
data[cols] = data[cols].apply(pd.to_numeric, errors="coerce")

n = 50
take_profit_pct = 0.05
stop_loss_pct = 0.03
commission = 0.001

data["Momentum"] = data["Close"] - data["Close"].shift(n)
data["Signal"] = 0
data.loc[data["Momentum"] > 0, "Signal"] = 1
data.loc[data["Momentum"] < 0, "Signal"] = -1

holding = False
entry_price = 0.0
trades = []

for i in range(1, len(data)):
    idx = data.index[i]
    close = data["Close"].iloc[i]
    high  = data["High"].iloc[i]
    low   = data["Low"].iloc[i]

    sig_now  = data["Signal"].iloc[i]
    sig_prev = data["Signal"].iloc[i - 1]

    if not holding:
        if sig_prev <= 0 and sig_now == 1:
            holding = True
            entry_price = close * (1 + commission)
            trades.append({
                "buy_date": idx,
                "buy_price": entry_price,
                "sell_date": None,
                "sell_price": None,
                "reason": None
            })
        continue


    tp_level = entry_price * (1 + take_profit_pct)
    sl_level = entry_price * (1 - stop_loss_pct)

    exit_now = False
    exit_price = None
    reason = None

    if low <= sl_level:
        exit_price = sl_level * (1 - commission)
        reason = "Stop Loss"
        exit_now = True

    elif high >= tp_level:
        exit_price = tp_level * (1 - commission)
        reason = "Take Profit"
        exit_now = True

    elif sig_prev >= 0 and sig_now == -1:
        exit_price = close * (1 - commission)
        reason = "Sell"
        exit_now = True

    if exit_now:
        holding = False
        trades[-1]["sell_date"] = idx
        trades[-1]["sell_price"] = exit_price
        trades[-1]["reason"] = reason



pnl_series = pd.Series(0.0, index=data.index)

for t in trades:
    if t["sell_date"] is not None:
        profit = t["sell_price"] - t["buy_price"]
        pnl_series.loc[t["sell_date"]] = profit

data["Profit"] = pnl_series.cumsum()


fig, (ax1, ax2) = plt.subplots(
    2, 1, 
    figsize=(17, 6), 
    sharex=True,
    gridspec_kw={'height_ratios': [3, 1]}
)

ax1.plot(data.index, data["Close"], label="Close Price", color="blue")


buy_dates  = [t["buy_date"]  for t in trades]
buy_prices = [t["buy_price"] for t in trades]

ax1.scatter(
    buy_dates,
    buy_prices,
    color="green",
    marker="^",
    label="Buy"
)
sell_dates  = [t["sell_date"]  for t in trades if t["reason"] == "Sell"]
sell_prices = [t["sell_price"] for t in trades if t["reason"] == "Sell"]

ax1.scatter(
    sell_dates,
    sell_prices,
    color="red",
    marker="v",
    label="Sell"
)

tp_dates  = [t["sell_date"]  for t in trades if t["reason"] == "Take Profit"]
tp_prices = [t["sell_price"] for t in trades if t["reason"] == "Take Profit"]

ax1.scatter(
    tp_dates,
    tp_prices,
    color="lime",
    marker="*",
    label="Take Profit"
)

sl_dates  = [t["sell_date"]  for t in trades if t["reason"] == "Stop Loss"]
sl_prices = [t["sell_price"] for t in trades if t["reason"] == "Stop Loss"]

ax1.scatter(
    sl_dates,
    sl_prices,
    color="red",
    marker="x",
    label="Stop Loss"
)


ax1.set_title("Momentum Strategy")
ax1.set_ylabel("Price")
ax1.grid(True)
ax1.legend()

ax2.plot(data.index, data["Momentum"], color="purple", label=f"Momentum ({n})")
ax2.axhline(0, color="black", linestyle="--")
ax2.set_title("Momentum Indicator")
ax2.set_xlabel("Date")
ax2.set_ylabel("Momentum")
ax2.grid(True)
ax2.legend()

plt.tight_layout()
plt.show()


# ===========================================================
plt.figure(figsize=(16, 6))
plt.plot(data.index, data["Profit"], color="green", label="Profit per share")
plt.title("Profit of 1 share (only on signals)")
plt.xlabel("Date")
plt.ylabel("Profit")
plt.axhline(0, color="black", linewidth=1)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

print(f"\nFINAL PROFIT: ${data['Profit'].iloc[-1]:,.2f}")


data["Trade_cost"] = 0.0
data.loc[data["Signal"].diff() != 0, "Trade_cost"] = data["Close"] * commission















# ===========================================================

# data["Daily_change"] = data["Close"].diff().fillna(0)
# data["Daily_profit"] = (data["Daily_change"] * data["Signal"].shift(1).fillna(0)) - data["Trade_cost"]
# data["All_profit"] = data["Daily_profit"].cumsum()

# plt.figure(figsize=(16, 6))
# plt.plot(data.index, data["Profit"], color="green", label="Profit per share")
# plt.title("Profit of 1 share (all)")
# plt.xlabel("Date")
# plt.ylabel("Profit")
# plt.axhline(0, color="black", linewidth=1)
# plt.grid(True)
# plt.legend()
# plt.tight_layout()
# plt.show()

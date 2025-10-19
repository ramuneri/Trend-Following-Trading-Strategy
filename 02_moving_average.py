# import pandas as pd
# import matplotlib.pyplot as plt

# data = pd.read_csv("AAPL.csv", parse_dates=["Date"])
# data.set_index("Date", inplace=True)

# # Convert numeric columns properly
# cols = ["Open", "High", "Low", "Close", "Volume"]
# data[cols] = data[cols].apply(pd.to_numeric, errors='coerce')

# short_window = 20
# long_window = 50

# data["SMA_short"] = data["Close"].rolling(window=short_window).mean()
# data["SMA_long"] = data["Close"].rolling(window=long_window).mean()

# plt.figure(figsize=(16, 7))
# plt.plot(data["Close"], label="Close Price", color="blue")
# plt.plot(data["SMA_short"], label=f"SMA {short_window}", color="green")
# plt.plot(data["SMA_long"], label=f"SMA {long_window}", color="red")

# plt.title("Trend Following: Moving Averages")
# plt.xlabel("Date")
# plt.ylabel("Price (USD)")
# plt.legend()
# plt.grid(True)
# plt.show()

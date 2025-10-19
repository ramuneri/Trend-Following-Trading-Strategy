import yfinance as yf
import pandas as pd

ticker = "AAPL"
start="2020-01-01"
end="2025-01-01"

data = yf.download(ticker, start=start, end=end, interval="1d", auto_adjust=True)
data = data[['Open', 'High', 'Low', 'Close', 'Volume']]

data.reset_index(inplace=True)
data.to_csv(f"{ticker}.csv", index=False)

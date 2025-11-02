import yfinance as yf

ticker = "AAPL"
start="2015-11-02"
end="2025-11-02"

data = yf.download(ticker, start=start, end=end, interval="1d", auto_adjust=False)
data = data[['Open', 'High', 'Low', 'Adj Close', 'Volume']]
data.rename(columns={'Adj Close': 'Close'}, inplace=True)

data.reset_index(inplace=True)
data.to_csv(f"{ticker}.csv", index=False)

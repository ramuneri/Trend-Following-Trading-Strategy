import yfinance as yf

ticker = "AAPL"
start="2020-11-02"
end="2025-11-02"

data = yf.download(ticker, start=start, end=end, interval="1d", auto_adjust=True)

data = data.reset_index() 
data.to_csv(f"{ticker}.csv", index=False)

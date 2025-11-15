# Momentum-Based Trading Strategy – Financial Intelligence Project

I used the **momentum indicator** as my trading strategy, but instead of using only the closing price, I used the **typical price** — the average of the high, low, and close — because it represents the middle of the day’s price movement

### Project Overview

This project implements a momentum-based trading strategy using historical stock price data and evaluates its performance through backtesting and parameter optimization.
The strategy is designed to demonstrate understanding of key financial concepts such as indicators, trading signals, portfolio simulation, and risk-adjusted performance measures.

### Objectives

Develop a trading strategy based on a previously created momentum indicator.
Simulate trades including take-profit, stop-loss, and commission costs.
Optimize the momentum period to maximize risk-adjusted returns (Sharpe ratio).
Visualize trading signals, portfolio growth, and the indicator over time.

### Methodology

Momentum Indicator

The momentum indicator measures the price change over a defined period 𝑛:

# Momentum(n) = Close(t) - Close(t-n)

#### Trading signals are generated as follows:

Buy Signal: Momentum crosses from negative to positive.
Sell Signal: Momentum crosses from positive to negative.

#### Optional risk management rules:

Take Profit: Close position when gain exceeds a fixed percentage.
Stop Loss: Close position when loss exceeds a fixed percentage.
Commission: Apply trading fees to each transaction.

## Sharpe ratio

How good your strategy’s returns are compared to its risk.

| Sharpe Ratio | Meaning               |
| ------------ | --------------------- |
| < 1.0        | Weak / risky strategy |
| 1.0–2.0      | Decent, acceptable    |
| 2.0–3.0      | Very good             |
| > 3.0        | Excellent and stable  |

Deviation (specifically standard deviation) means how much something moves away from its average.

How the code works:

- Calculates average daily return
- Divides by daily volatility
- Converts to annual scale

### Extra:

Extra - mini strategija.
Prasukti ciklą, prabėgti per duomenis, padaryti paprastą indikatorių.
1 slenkančio vidurkio pvz. - kai kaina aukštesnė už tą slenkantį vidurkį - nusiperki, jei žemesnė - parduodi.

### Notes:

When the buy or sell signal appears, I enter the trade at a middle price between yesterday’s close and today’s close, because the signal is generated only after the entire daily candle is completed, and the exact intraday price of the signal is unknown.

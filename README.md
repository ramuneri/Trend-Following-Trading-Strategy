# Momentum-Based Trading Strategy – Financial Intelligence Project

### Project Overview

This project implements a momentum-based trading strategy using historical stock price data and evaluates its performance through backtesting and parameter optimization.
The strategy is designed to demonstrate understanding of key financial concepts such as indicators, trading signals, portfolio simulation, and risk-adjusted performance measures.

### Objectives

Develop a trading strategy based on a previously created momentum indicator.
Simulate trades including take-profit, stop-loss, and commission costs.
Optimize the momentum period to maximize risk-adjusted returns (Sharpe ratio).
Visualize trading signals, portfolio growth, and the indicator over time.

### Methodology

3.1 Momentum Indicator

The momentum indicator measures the price change over a defined period 𝑛.

# Momentum(n) = Close(t) - Close(t-n)

#### Trading signals are generated as follows:

Buy Signal: Momentum crosses from negative to positive.
Sell Signal: Momentum crosses from positive to negative.

#### Optional risk management rules:

Take Profit: Close position when gain exceeds a fixed percentage.
Stop Loss: Close position when loss exceeds a fixed percentage.
Commission: Apply trading fees to each transaction.

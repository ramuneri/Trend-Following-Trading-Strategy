# Trend-Following Trading Strategy in Python

## Description

This project demonstrates the creation, simulation, and optimization of a **trend-following** trading strategy using Python.  
The strategy uses **moving average crossovers** to generate buy and sell signals, includes **take profit and stop loss mechanisms**, accounts for **transaction costs**, and evaluates performance through an equity curve and Sharpe ratio optimization.

## Features

- Trend-following strategy based on moving averages
- Buy/sell signals with annotations on price charts
- Take profit and stop loss for risk management
- Transaction costs included in profit calculations
- Parameter optimization using brute-force or random search
- Performance evaluation with equity curve and Sharpe ratio

## Technologies Used

- Python
- pandas
- numpy
- matplotlib
- yfinance

## Strategy

##### IF short_MA > long_MA → we are in an uptrend → buy or hold

- The short MA is above the long MA, meaning recent prices are higher than older prices.
- This signals momentum upward — trend-following strategy assumes the price will continue rising.
  Actions:
- If you are not in a position → buy
- If you are already holding → do nothing (hold)

##### IF short_MA < long_MA → we are in a downtrend → sell or stay out

- The short MA is below the long MA, meaning recent prices are lower than older prices.
- This signals momentum downward — the trend is falling.

##### Actions:

- If you are holding → sell to avoid losses
- If you are not holding → stay out

##### Portfolio price changes

🔼 Buy → sharp jump (cash → stock)
📈 Hold → wiggly line (portfolio follows price)
🔽 Sell → sharp drop (stock → cash)
— Flat → straight line (holding cash)

TODO

- fix names with .csv

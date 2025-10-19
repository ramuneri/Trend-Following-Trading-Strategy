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

IF short_MA > long_MA → we are in an uptrend → buy or hold
IF short_MA < long_MA → we are in a downtrend → sell or stay out

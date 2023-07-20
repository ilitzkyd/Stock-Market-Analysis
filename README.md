# Stock Correlation and Economic Indicators

This Jupyter notebook contains two classes, `StockAnalysis` and `CorrelationVisualizer`, designed to help with the analysis of stock data and visualization of correlations between stock prices and economic indicators.

## Stock Analysis

The `StockAnalysis` class fetches historical stock data from Yahoo Finance, calculates Bollinger Bands, identifies bullish and bearish signals, and creates visualizations using Plotly.

### Requirements

- Python 3.x
- pandas
- yfinance
- plotly
- prophet

### Usage

1. Open the `stock_correlation_economic_indicators.ipynb` notebook.
2. Make sure you have the required libraries installed (you can install them using `!pip install pandas yfinance plotly prophet`).
3. In the `StockAnalysis` class, initialize the object with your desired list of stock tickers and the date range for historical data.
4. Run the cells to perform the analysis and visualize the results.

## Correlation Visualizer

The `CorrelationVisualizer` class fetches economic indicator data from FRED API and stock price data from Yahoo Finance for the specified tickers. It then calculates the correlation matrix and visualizes it using Seaborn.

### Requirements

- Python 3.x
- pandas
- yfinance
- seaborn
- matplotlib
- fredapi

### Usage

1. Open the `stock_correlation_economic_indicators.ipynb` notebook.
2. Make sure you have the required libraries installed (you can install them using `!pip install pandas yfinance seaborn matplotlib fredapi`).
3. In the `CorrelationVisualizer` class, initialize the object with your desired list of stock tickers, economic indicators, and the date range for data.
4. Obtain your FRED API key from https://fred.stlouisfed.org/docs/api/api_key.html.
5. Replace `'YOUR_FRED_API_KEY'` in the notebook with your actual API key.
6. Run the cells to fetch data and visualize the correlation matrix for each ticker and the economic indicators.

### Bearish and Bullish Signals

In the `StockAnalysis` class, Bollinger Bands are calculated based on a rolling average and standard deviation of the closing prices. When the closing price crosses above the upper Bollinger Band, it's considered a **bearish signal**, indicating a potential overbought condition. Conversely, when the closing price crosses below the lower Bollinger Band, it's considered a **bullish signal**, indicating a potential oversold condition.

The `identify_bullish_bearish_signals` method in the `StockAnalysis` class identifies these bullish and bearish signals, and they are visualized as green and red markers on the plot.

## Examples

For examples and usage, please see the code in the `stock_correlation_economic_indicators.ipynb` notebook.

## Note

Please make sure you have the required libraries installed before running the code. If you encounter any issues, feel free to contribute to the project or create issues on GitHub.

Make sure to replace `'YOUR_FRED_API_KEY'` in the notebook with your actual FRED API key to fetch economic indicator data.

Happy analyzing and visualizing!

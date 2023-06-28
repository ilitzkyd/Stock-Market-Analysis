import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
from arch import arch_model
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error
from scipy.stats import boxcox

# Set start and end dates
start = pd.to_datetime("2019-05-01")
end = pd.to_datetime("2021-10-28")

# Get stock data using pandas-datareader
import pandas_datareader.data as web
stock_symbols = ["GOOG", "SCCO", "WHR"]
data = web.DataReader(stock_symbols, data_source="yahoo", start=start, end=end)["Adj Close"]

# Single stock analysis
stocks = pd.DataFrame(data["GOOG"])  # Selecting the "GOOG" stock
stocks.columns = ["Price"]

# Manual ARIMA model
myts = stocks.resample("M").last()  # Resample to monthly frequency
myts.index = pd.DatetimeIndex(myts.index.to_period("M").to_timestamp())
myts = myts.squeeze()  # Convert to a Series

model = ARIMA(myts, order=(1, 0, 0))  # ARIMA model with order (1, 0, 0)
results = model.fit()

forecast = results.forecast(steps=12)  # Forecast 12 steps ahead
forecast_index = pd.date_range(start=myts.index[-1] + pd.DateOffset(months=1), periods=12, freq="M")
forecast = pd.Series(forecast[0], index=forecast_index)

# Plotting the forecast
plt.figure(figsize=(10, 6))
plt.plot(myts, label="Actual")
plt.plot(forecast, label="Forecast", linestyle="--")
plt.fill_between(forecast.index, forecast - 2 * forecast.std(), forecast + 2 * forecast.std(), alpha=0.2)
plt.title("GOOGL Stock Price Forecast")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.show()

# ARIMA using auto.arima
def function_ets(x):
    model = sm.tsa.ExponentialSmoothing(x)
    fit_model = model.fit()
    forecast = fit_model.forecast(steps=1)
    return forecast[0]

def function_arima(x):
    model = sm.tsa.arima.ARIMA(x, order=(1, 0, 0))
    fit_model = model.fit()
    forecast = fit_model.forecast(steps=1)
    return forecast[0]

arima_limit = stocks.loc[start:end, "Price"]
ts1 = []
ts2 = []

for i in range(1, len(arima_limit)):
    ts1.append(function_ets(arima_limit[:i]))
    ts2.append(function_arima(arima_limit[:i]))

mse_model1 = mean_squared_error(arima_limit[1:], ts1)
mse_model2 = mean_squared_error(arima_limit[1:], ts2)

# GARCH
stocks_adj = pd.DataFrame({
    "Price": data["GOOG"],
    "Return": np.log(data["GOOG"]).diff()
}).dropna()

garch_model = arch_model(stocks_adj["Return"], vol="Garch", p=1, q=1)
fit_garch = garch_model.fit()

fit_garch.plot()
plt.show()

# KNN
df = pd.DataFrame({
    "ds": data["GOOG"].index,
    "y": data["GOOG"].values
})

knn_forecast = KNeighborsRegressor(n_neighbors=40)
knn_forecast.fit(df[["ds"]], df["y"])
predknn = knn_forecast.predict(df[["ds"]])

plt.figure(figsize=(10, 6))
plt.plot(df["ds"], df["y"], label="Actual")
plt.plot(df["ds"], predknn, label="Forecast", linestyle="--")
plt.title("KNN Forecast")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.show()

# Neural network
alpha = 1.5 ** (-10)
hn = len(stocks) / (alpha * (len(stocks) + 30))
lambda_val, _ = boxcox(stocks["Price"])  # Box-Cox transformation
neural_pred = sm.tsa.ARIMA(stocks["Price"], order=(hn, 0, 0), trend="n", enforce_invertibility=False)
neural_pred_fit = neural_pred.fit(disp=False)
neural_forecast = neural_pred_fit.forecast(steps=30)

# Accuracy of the models
print("Accuracy of Manual ARIMA:")
print(neural_pred_fit.summary())
print()

print("Accuracy of auto.arima:")
print("MSE for model1: ", mse_model1)
print("MSE for model2: ", mse_model2)
print()

print("Accuracy of GARCH:")
print(fit_garch.summary())
print()

print("Accuracy of KNN:")
print("MSE: ", mean_squared_error(df["y"], predknn))
print()

print("Accuracy of Neural Network:")
print("MSE: ", mean_squared_error(stocks["Price"].iloc[-30:], neural_forecast[0]))
print()

# Correlation analysis
df_correlation = pd.DataFrame({
    "WHR.Adjusted": data["WHR"],
    "SCCO.Adjusted": data["SCCO"]
})

correlation_matrix = df_correlation.corr()
correlation_coefficient = correlation_matrix.loc["WHR.Adjusted", "SCCO.Adjusted"]

print("Correlation Coefficient: ", correlation_coefficient)

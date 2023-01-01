import pandas as pd

# MACD Analysis
def func_macd (history):

        # Calculate the MACD using the close prices
        fast_period = 12
        slow_period = 26
        signal_period = 9
        # Calculate the fast and slow moving averages
        fast_ma = history["Close"].ewm(span=fast_period, adjust=False).mean()
        slow_ma = history["Close"].ewm(span=slow_period, adjust=False).mean()
        # Calculate the MACD line
        macd_line = fast_ma - slow_ma
        # Calculate the MACD signal line
        macd_signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        # Calculate the MACD histogram
        macd_hist = macd_line - macd_signal_line
        # Create a table to store the results
        results = pd.DataFrame(columns=["Analysis", "Description", "Recommendation"])
        # Add a row to the table with the results of the MACD analysis
        macd_results = pd.concat([results, pd.DataFrame({"Analysis": "MACD",
                                                         "Description": "The MACD is a trend-following momentum indicator that shows the relationship between two moving averages of a stock's price. A bullish MACD indicates that the stock is likely to continue rising, while a bearish MACD indicates that the stock is likely to continue falling.",
                                                         "Recommendation": "Buy" if list(macd_hist)[-1] > 0 else "Sell"}, index=[0])], ignore_index=True)
        return macd_results

# Bollinger Bands Analysis
def bb_func(history):

    # Calculate the Bollinger Bands using the close prices
    timeperiod = 20
    nbdevup = 2
    nbdevdn = 2
    matype = 0

    # Calculate the rolling mean and standard deviation of the close prices
    rolling_mean = history["Close"].rolling(window=timeperiod).mean()
    rolling_std = history["Close"].rolling(window=timeperiod).std()

    # Calculate the upper and lower Bollinger Bands
    upper_band = rolling_mean + nbdevup * rolling_std
    lower_band = rolling_mean - nbdevdn * rolling_std

    # Create a table to store the results
    results = pd.DataFrame(columns=["Analysis", "Description", "Recommendation"])

    # Add a row to the table with the results of the Bollinger Bands analysis
    if list(history["Close"])[-1] > list(upper_band)[-1]:
        recommendation = "Sell"
    elif list(history["Close"])[-1] < list(lower_band)[-1]:
        recommendation = "Buy"
    else:
        recommendation = "Hold"

    bb_results = pd.concat([results, pd.DataFrame({"Analysis": "Bollinger Bands",
                                                   "Description": "Bollinger Bands are a technical analysis tool that uses moving averages and standard deviations to indicate overbought or oversold conditions in a stock. When the stock price is above the upper band, it is considered overbought, and when the stock price is below the lower band, it is considered oversold.",
                                                   "Recommendation": recommendation}, index=[0])], ignore_index=True)
    return bb_results


# RSI Analysis
def rsi_func(history):

    # Calculate the RSI using the close prices
    timeperiod = 14

    # Calculate the difference between the current close price and the previous close price
    diff = history["Close"].diff()

    # Calculate the up and down movements
    up_movements = diff.where(diff > 0, 0)
    down_movements = diff.where(diff < 0, 0)

    # Calculate the average up and down movements over the past timeperiod periods
    avg_up_movement = up_movements.rolling(timeperiod).mean()
    avg_down_movement = down_movements.rolling(timeperiod).mean().abs()

    # Calculate the relative strength
    relative_strength = avg_up_movement / avg_down_movement

    # Calculate the RSI
    rsi = 100 - (100 / (1 + relative_strength))

    # Create a table to store the results
    results = pd.DataFrame(columns=["Analysis", "Description", "Recommendation"])

    # Add a row to the table with the results of the RSI analysis
    if list(rsi)[-1] > 70:
        recommendation = "Sell"
    elif list(rsi)[-1] < 30:
        recommendation = "Buy"
    else:
        recommendation = "Hold"


    rsi_results = pd.concat([results, pd.DataFrame({"Analysis": "Relative Strength Index (RSI)",
                                                    "Description": "The Relative Strength Index (RSI) is a momentum indicator that measures the strength of a stock's price movement. A reading above 70 indicates that the stock is overbought and may be due for a correction, while a reading below 30 indicates that the stock is oversold and may be a good buying opportunity.",
                                                    "Recommendation": recommendation}, index=[0])], ignore_index=True)
    return rsi_results

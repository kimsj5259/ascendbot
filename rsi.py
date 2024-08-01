import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Function to calculate RSI
def calculate_rsi(data, window=14):
    delta = data.diff().dropna()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Load example cryptocurrency price data (replace with your own data)
# Example data (Bitcoin daily closing prices)
data = pd.DataFrame({
    'Date': pd.date_range(start='2022-01-01', periods=100),
    'Close': np.random.randint(10000, 60000, 100)  # Replace with your own data
})
data.set_index('Date', inplace=True)

# Calculate RSI with a default window of 14 periods
data['RSI'] = calculate_rsi(data['Close'])

# Plotting RSI and overbought/oversold levels (typically 70 and 30)
plt.figure(figsize=(12, 6))
plt.plot(data.index, data['RSI'], label='RSI', color='blue')
plt.axhline(y=70, color='red', linestyle='--', label='Overbought (>70)')
plt.axhline(y=30, color='green', linestyle='--', label='Oversold (<30)')
plt.title('Relative Strength Index (RSI)')
plt.xlabel('Date')
plt.ylabel('RSI')
plt.legend()
plt.show()

# Generating buy/sell signals based on RSI thresholds (e.g., 30 and 70)
data['Buy_Signal'] = np.where(data['RSI'] < 30, 1, 0)
data['Sell_Signal'] = np.where(data['RSI'] > 70, -1, 0)

# Displaying the buy/sell signals
print(data[['RSI', 'Buy_Signal', 'Sell_Signal']])


#%%
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# List of the stocks
stocks = ['BOSS.DE', 'RL', 'PVH', 'PUM.DE', 'NKE', 'ADS.DE', 'LEVI', "LVMUY"]

# Date range
start_date = '2021-06-03'
end_date = '2023-10-16'

# Download the data
data = yf.download(stocks, start=start_date, end=end_date, interval='1wk')

# Select only Close price
data = data['Close']

# Replace missing values with previous ones
data.fillna(method='ffill', inplace=True)

# Normalize to 100 at the beginning of the period
data_normalized = data.div(data.iloc[0]).mul(100)

# Print normalized data
print(data_normalized)

# Parse the start date and get the month and year in three letter abbreviation
start_date_parsed = datetime.strptime(start_date, "%Y-%m-%d")
start_date_str = start_date_parsed.strftime("%b %Y").upper()

# Plot the data
data_normalized.plot(figsize=(14,7))
plt.title('Normalized Stock Prices')
plt.ylabel(f'Price ({start_date_str} = 100)')
plt.grid()
plt.show()

#%%
data_normalized.to_excel("20231025_stock_performance.xlsx")
# %%

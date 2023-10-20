import pandas as pd
import numpy as np

# Create a dataset simulating hourly water consumption for a day
hours = list(range(0,24))  # 24 hours in a day
np.random.seed(42)  # To ensure reproducibility

# Adjust consumption to sum up to max 3 liters
consumption = np.random.uniform(0.05, 0.15, 24)

# Assuming no consumption between 1am to 8am
for hour in range(1, 9):
    consumption[hour] = 0

cumulative_consumption = (3 * consumption.cumsum()) / consumption.sum() 
df_hourly = pd.DataFrame({'Hour': hours, 'Cumulative Consumption (L)': cumulative_consumption})

file_path = "water_consumption_day.csv"
df_hourly.to_csv(file_path, index=False)

print(f"Data saved to {file_path}")


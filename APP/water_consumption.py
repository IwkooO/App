import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

# Generate date range for a month (30 days)
date_range = pd.date_range(start="2023-09-01", periods=30, freq="D")

# Generate water consumption data: range between 1.8 to 2.7 liters
water_consumption = np.random.uniform(1.8, 2.7, 30)

# Create a DataFrame
df = pd.DataFrame({
    'Date': date_range,
    'Water Consumption (L)': water_consumption
})

# Save to CSV
file_path = "water_consumption.csv"
df.to_csv(file_path, index=False)

print(f"Data saved to {file_path}")

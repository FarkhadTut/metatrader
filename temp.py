import pandas as pd

# Example hourly dataframe
df_hourly = pd.DataFrame({
    'date_hourly': pd.date_range('2024-01-01', periods=10, freq='H'),
    'hourly_price': range(10)
})

# Example daily dataframe
df_daily = pd.DataFrame({
    'date_daily': pd.date_range('2024-01-01', periods=3, freq='D'),
    'daily_price': range(3)
})

# Merge hourly and daily dataframes
df_hourly['date_daily'] = df_hourly['date_hourly'].dt.date
# df = pd.merge(df_hourly, df_daily, on='date_daily')
df= pd.concat([df_daily, df_hourly], axis=1)

# Drop the date_daily column if you don't need it
df = df.drop('date_daily', axis=1)

# Check the first 10 rows
print(df.head(10))

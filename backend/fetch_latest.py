# fetch_latest.py

import pandas as pd
import requests
import numpy as np
from datetime import datetime
from config import TIINGO_API_KEY, DATA_PATH


# -------------------- Manual Indicator Calculations --------------------

def calculate_latest_indicators(existing_df, latest_df):
    """Calculate indicators for the new latest record based on previous data."""
    print("📊 Calculating indicators for the latest record...")

    # Combine existing data with the new latest record temporarily
    temp_df = pd.concat([existing_df, latest_df])

    # MACD (12, 26, 9) Calculation
    temp_df['EMA_12'] = temp_df['close'].ewm(span=12, adjust=False).mean()
    temp_df['EMA_26'] = temp_df['close'].ewm(span=26, adjust=False).mean()
    temp_df['MACD'] = temp_df['EMA_12'] - temp_df['EMA_26']
    temp_df['Signal'] = temp_df['MACD'].ewm(span=9, adjust=False).mean()
    temp_df['Histogram'] = temp_df['MACD'] - temp_df['Signal']

    # RSI (14) Calculation
    delta = temp_df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    temp_df['RSI'] = 100 - (100 / (1 + rs))

    # EMA (30 and 120) Calculation
    temp_df['EMA 30'] = temp_df['close'].ewm(span=30, adjust=False).mean()
    temp_df['EMA 120'] = temp_df['close'].ewm(span=120, adjust=False).mean()

    # Drop intermediate columns
    temp_df = temp_df.drop(columns=['EMA_12', 'EMA_26'])

    # Drop NaN rows generated during calculations
    temp_df = temp_df.dropna()

    # Return only the latest record with calculated indicators
    latest_df_with_indicators = temp_df.tail(1)

    return latest_df_with_indicators


# -------------------- Fetch Latest Record and Append --------------------

def fetch_latest_record(target_date="2025-02-21T20:00:00"):
    """Fetch a specific hourly forex record using Tiingo API and append it to the CSV."""
    print(f"📡 Fetching the latest record for {target_date}...")

    url = "https://api.tiingo.com/tiingo/fx/EURUSD/prices"

    params = {
        'token': TIINGO_API_KEY,
        'resampleFreq': '1hour',
        'startDate': target_date,
        'endDate': target_date,
        'columns': 'date,open,high,low,close,volume'
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()

        # Debug print
        print(f"✅ API call successful. Records received: {len(data)}")

        if len(data) == 0:
            print("⚠️ No data returned. Check the date or API.")
            return

        # Convert to DataFrame
        latest_df = pd.DataFrame(data)
        latest_df['date'] = pd.to_datetime(latest_df['date'])
        latest_df.set_index('date', inplace=True)

        # Debug print
        print(latest_df)

        # -------------------- Append Latest Record to CSV --------------------
        # Read existing CSV file (all existing records)
        existing_df = pd.read_csv(DATA_PATH)
        existing_df['date'] = pd.to_datetime(existing_df['date'])
        existing_df.set_index('date', inplace=True)

        # Calculate indicators only for the latest record using previous data
        latest_df_with_indicators = calculate_latest_indicators(existing_df, latest_df)

        # Append the new row as the 61st row (without altering previous rows)
        updated_df = pd.concat([existing_df, latest_df_with_indicators])

        # Save back to CSV
        updated_df.to_csv(DATA_PATH, mode='w', index=True)
        print(f"✅ Latest record for {target_date} appended and saved at: {DATA_PATH}")

        # Return the appended record as JSON
        return latest_df_with_indicators.to_dict(orient="records")[0]

    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return None


if __name__ == '__main__':
    fetch_latest_record()

# fetch_data.py

import pandas as pd
import requests
import numpy as np
from datetime import datetime, timedelta
from config import TIINGO_API_KEY, DATA_PATH


# -------------------- Manual Indicator Calculations --------------------

def calculate_indicators(df):
    """Calculate MACD, Signal, Histogram, RSI, and EMA manually using Pandas."""
    print("Calculating technical indicators...")

    # MACD (12, 26, 9) Calculation
    df['EMA_12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['Histogram'] = df['MACD'] - df['Signal']

    # RSI (14) Calculation
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # EMA (30 and 120) Calculation
    df['EMA 30'] = df['close'].ewm(span=30, adjust=False).mean()
    df['EMA 120'] = df['close'].ewm(span=120, adjust=False).mean()

    # Drop intermediate columns
    df = df.drop(columns=['EMA_12', 'EMA_26'])

    # Drop NaN rows generated during calculations
    df = df.dropna()

    return df


# -------------------- Main Data Fetching --------------------

def fetch_data():
    """Fetch the last 130 hourly records using Tiingo API and save the last 60 locally."""
    print("📡 Fetching historical data...")

    url = "https://api.tiingo.com/tiingo/fx/EURUSD/prices"

    # Fetch 130 hourly records to account for indicator calculations
    end_date = "2025-02-21T19:00:00"
    start_date = (datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S') - timedelta(hours=130)).strftime('%Y-%m-%dT%H:%M:%S')

    params = {
        'token': TIINGO_API_KEY,
        'resampleFreq': '1hour',
        'startDate': start_date,
        'endDate': end_date,
        'columns': 'date,open,high,low,close,volume'
    }

    # Debug print
    print(f"🗓️ Fetching data from {start_date} to {end_date}")

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()

        # Debug print
        print(f"✅ API call successful. Records received: {len(data)}")

        if len(data) == 0:
            print("⚠️ No data returned by the API. Check the date range or API key.")
            return

        # Convert to DataFrame
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

        # Debug print
        print(df.head())

        # -------------------- Calculate Indicators --------------------
        df = calculate_indicators(df)

        # Save only the last 60 rows
        df = df.tail(60)

        # Debug print
        print(f"✅ After calculations, remaining rows: {len(df)}")

        # Save locally
        df.to_csv(DATA_PATH)
        print(f"✅ Data fetched and saved locally at: {DATA_PATH}")

    else:
        print(f"❌ Error: {response.status_code} - {response.text}")


if __name__ == '__main__':
    fetch_data()

import yfinance as yf
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def fetch_stock_data(symbol, start_date, end_date):
    """Fetch stock data for a given symbol and date range."""
    stock = yf.Ticker(symbol)
    data = stock.history(start=start_date, end=end_date)
    return data

def calculate_metrics(df):
    """Calculate financial metrics."""
    df['Daily_Return'] = df['Close'].pct_change()
    df['Cumulative_Return'] = (1 + df['Daily_Return']).cumprod() - 1
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    
    # Total Return
    total_return = df['Cumulative_Return'].iloc[-1]
    
    # Volatility (annualized)
    volatility = df['Daily_Return'].std() * np.sqrt(252)
    
    # Sharpe Ratio (assuming risk-free rate of 0 for simplicity)
    sharpe_ratio = (df['Daily_Return'].mean() * 252) / volatility
    
    # Add these metrics to the dataframe
    df['Total_Return'] = total_return
    df['Volatility'] = volatility
    df['Sharpe_Ratio'] = sharpe_ratio
    
    return df

def load_to_database(df, table_name, engine):
    """Load data to the SQL database."""
    df.to_sql(table_name, engine, if_exists='replace', index=True)

def main():
    # List of Indian stock symbols
    symbols = ['TATAMOTORS.NS', 'TATASTEEL.NS', 'TATAPOWER.NS']
    start_date = '2020-01-01'
    end_date = '2023-12-31'

    # Create database engine
    engine = create_engine('sqlite:///indian_stock_data.db')

    for symbol in symbols:
        print(f"Processing {symbol}...")
        
        # Extract
        data = fetch_stock_data(symbol, start_date, end_date)
        
        # Transform
        data = calculate_metrics(data)
        
        # Load
        load_to_database(data, f"{symbol.replace('.NS', '')}_data", engine)

    print("Data processing complete.")

if __name__ == "__main__":
    main()
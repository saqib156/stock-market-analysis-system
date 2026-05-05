import yfinance as yf
import pandas as pd

class StockDataFetcher:
    """
    Role: Retrieves historical stock price data.
    """
    def __init__(self):
        pass

    def fetchHistoricalData(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetches historical stock prices using the yfinance API.
        
        Args:
            symbol (str): The stock ticker symbol (e.g., 'AAPL').
            start_date (str): Start date in 'YYYY-MM-DD' format.
            end_date (str): End date in 'YYYY-MM-DD' format.
            
        Returns:
            pd.DataFrame: A pandas DataFrame containing the historical stock data.
                          Returns None if fetching fails or data is empty.
        """
        try:
            print(f"Fetching data for {symbol} from {start_date} to {end_date}...")
            # Download the data from Yahoo Finance
            data = yf.download(symbol, start=start_date, end=end_date, progress=False)
            
            # Check if the dataframe is empty
            if data is None or data.empty:
                print(f"No data found for {symbol} in the given date range.")
                return None
            
            return data
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None

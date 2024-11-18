import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging
from .db_manager import DatabaseManager

logger = logging.getLogger(__name__)

class StockDataCollector:
    def __init__(self):
        self.db = DatabaseManager()

    def get_stock_data(self, symbol: str, period: str = "3mo") -> pd.DataFrame:
        """
        Get stock data for a given symbol. First tries to get from local database,
        if not available or outdated, fetches from yfinance.
        
        :param symbol: Stock symbol (e.g., 'RELIANCE.NS')
        :param period: Time period for data (e.g., '3mo', '1y')
        :return: DataFrame with stock data
        """
        try:
            # Calculate date range based on period
            end_date = datetime.now()
            if period == "3mo":
                start_date = end_date - timedelta(days=90)
            elif period == "1y":
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=90)  # default to 3mo
            
            # Try to get data from database first
            if self.db.is_data_fresh(symbol):
                df = self.db.get_stock_data(symbol, start_date, end_date)
                if df is not None and not df.empty:
                    logger.info(f"Retrieved {symbol} data from database")
                    return df
            
            # If not in database or outdated, fetch from yfinance
            logger.info(f"Fetching {symbol} data from yfinance")
            stock = yf.Ticker(symbol)
            df = stock.history(period=period)
            
            # Save to database
            if not df.empty:
                self.db.save_stock_data(symbol, df)
                logger.info(f"Saved {symbol} data to database")
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return pd.DataFrame()  # Return empty DataFrame on error

    def get_multiple_stock_data(self, symbols: list, period: str = "3mo") -> dict:
        """
        Get stock data for multiple symbols
        
        :param symbols: List of stock symbols
        :param period: Time period for data
        :return: Dictionary of DataFrames with stock data
        """
        data = {}
        for symbol in symbols:
            data[symbol] = self.get_stock_data(symbol, period)
        return data

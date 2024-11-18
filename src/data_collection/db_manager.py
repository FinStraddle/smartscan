import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import logging
import os

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        # Get the absolute path to the project root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        
        # Create data directory in project root
        self.db_dir = os.path.join(project_root, 'data')
        os.makedirs(self.db_dir, exist_ok=True)
        
        self.db_path = os.path.join(self.db_dir, 'stock_data.db')
        self._init_db()

    def _init_db(self):
        """Initialize the database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create stock data table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS stock_data (
                        symbol TEXT,
                        date DATE,
                        open REAL,
                        high REAL,
                        low REAL,
                        close REAL,
                        volume INTEGER,
                        last_updated TIMESTAMP,
                        PRIMARY KEY (symbol, date)
                    )
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise

    def get_stock_data(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Retrieve stock data from the database
        Returns None if data is not found or is outdated
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = '''
                    SELECT date, open, high, low, close, volume
                    FROM stock_data
                    WHERE symbol = ? AND date BETWEEN ? AND ?
                    ORDER BY date
                '''
                
                df = pd.read_sql_query(
                    query, 
                    conn,
                    params=(symbol, start_date.date(), end_date.date()),
                    parse_dates=['date']
                )
                
                if len(df) > 0:
                    df.set_index('date', inplace=True)
                    return df
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving data for {symbol}: {str(e)}")
            return None

    def save_stock_data(self, symbol: str, data: pd.DataFrame):
        """Save stock data to the database"""
        try:
            if data is None or data.empty:
                logger.warning(f"No data to save for {symbol}")
                return

            with sqlite3.connect(self.db_path) as conn:
                # Prepare data for insertion
                df_to_save = data.reset_index()
                df_to_save['symbol'] = symbol
                df_to_save['last_updated'] = datetime.now()
                
                # Insert data
                df_to_save.to_sql('stock_data', conn, if_exists='replace', index=False)
                logger.info(f"Successfully saved data for {symbol}")
                
        except Exception as e:
            logger.error(f"Error saving data for {symbol}: {str(e)}")
            raise

    def is_data_fresh(self, symbol: str, lookback_days: int = 1) -> bool:
        """Check if we have fresh data for the symbol"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get the latest data date and last update timestamp
                query = '''
                    SELECT MAX(date), MAX(last_updated)
                    FROM stock_data
                    WHERE symbol = ?
                '''
                
                cursor.execute(query, (symbol,))
                latest_date, last_updated = cursor.fetchone()
                
                if latest_date is None or last_updated is None:
                    return False
                
                # Convert to IST (UTC+5:30)
                ist_now = datetime.now() + timedelta(hours=5, minutes=30)
                last_updated = datetime.strptime(last_updated, '%Y-%m-%d %H:%M:%S.%f')
                latest_date = datetime.strptime(latest_date, '%Y-%m-%d').date()
                
                # If it's before 5:30 PM IST, we can use yesterday's data
                cutoff_time = ist_now.replace(hour=17, minute=30, second=0, microsecond=0)
                if ist_now < cutoff_time:
                    latest_required_date = (ist_now - timedelta(days=2)).date()
                else:
                    latest_required_date = (ist_now - timedelta(days=1)).date()
                
                return latest_date >= latest_required_date
                
        except Exception as e:
            logger.error(f"Error checking data freshness for {symbol}: {str(e)}")
            return False

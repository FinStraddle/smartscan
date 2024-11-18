import yfinance as yf
import pandas as pd
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_nifty50_symbols():
    """
    Read Nifty 50 symbols from CSV file
    :return: List of Nifty 50 symbols with '.NS' appended
    """
    try:
        # Get the absolute path to the project root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        csv_path = os.path.join(project_root, 'src', 'nse_stock_lists', 'ind_nifty50list.csv')
        
        df = pd.read_csv(csv_path)
        symbols = df['Symbol'].tolist()
        
        # Special cases mapping for Yahoo Finance
        symbol_mapping = {
            'RELIANCE': 'RELIANCE.BO',  # Try BSE symbol
            'M&M': 'M&M.BO',  # Try BSE symbol for Mahindra
            'TATAMOTORS': 'TATAMOTORS.BO',  # Try BSE symbol
            'MARUTI': 'MARUTI.BO',  # Try BSE symbol
            'BAJAJ-AUTO': 'BAJAJ-AUTO.BO'  # Try BSE symbol
        }
        
        # Add .NS suffix only for non-special cases
        return [symbol_mapping.get(symbol, symbol + '.NS') for symbol in symbols]
    except FileNotFoundError:
        logger.error(f"Error: CSV file not found at {csv_path}")
        return []
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        return []

def fetch_stock_data(ticker, symbol, default_period="3mo"):
    """
    Attempt to fetch stock data with different time periods
    :param ticker: yfinance Ticker object
    :param symbol: Stock symbol
    :param default_period: Default time period to try first
    :return: Tuple of (DataFrame, period_used)
    """
    # Try different periods in sequence
    periods = [default_period, "ytd", "1y", "max"]
    
    for period in periods:
        try:
            stock_data = ticker.history(period=period)
            if not stock_data.empty:
                logger.info(f"Successfully fetched {symbol} data using period: {period}")
                # If using a longer period, trim to match default_period
                if period != default_period:
                    end_date = pd.Timestamp.now()
                    if default_period == "3mo":
                        start_date = end_date - pd.DateOffset(months=3)
                    elif default_period == "1mo":
                        start_date = end_date - pd.DateOffset(months=1)
                    else:
                        start_date = end_date - pd.DateOffset(days=90)  # fallback to 90 days
                    
                    stock_data = stock_data.loc[start_date:end_date]
                
                return stock_data, period
        except Exception as e:
            logger.warning(f"Failed to fetch {symbol} with period {period}: {e}")
    
    return pd.DataFrame(), None

def fetch_nifty50_data(period="3mo"):
    """
    Fetch data for Nifty 50 stocks
    :param period: Time period to fetch data for (e.g., "1d", "1mo", "1y")
    :return: Dictionary of DataFrames with stock data
    """
    nifty50_symbols = get_nifty50_symbols()

    if not nifty50_symbols:
        logger.error("No symbols found. Please check the CSV file.")
        return {}

    data = {}
    for symbol in nifty50_symbols:
        try:
            # Try NSE/BSE symbol first
            stock = yf.Ticker(symbol)
            stock_data, used_period = fetch_stock_data(stock, symbol, period)
            
            if stock_data.empty:
                logger.warning(f"No data available for {symbol}")
                # Try alternative formats
                if '.NS' in symbol:
                    # Try BSE symbol
                    bse_symbol = symbol.replace('.NS', '.BO')
                    stock = yf.Ticker(bse_symbol)
                    stock_data, used_period = fetch_stock_data(stock, bse_symbol, period)
                    if not stock_data.empty:
                        symbol = bse_symbol
                elif '.BO' in symbol:
                    # Try NSE symbol
                    nse_symbol = symbol.replace('.BO', '.NS')
                    stock = yf.Ticker(nse_symbol)
                    stock_data, used_period = fetch_stock_data(stock, nse_symbol, period)
                    if not stock_data.empty:
                        symbol = nse_symbol
                
                # If still no data, try base symbol
                if stock_data.empty:
                    base_symbol = symbol.replace('.NS', '').replace('.BO', '')
                    stock = yf.Ticker(base_symbol)
                    stock_data, used_period = fetch_stock_data(stock, base_symbol, period)
                    if not stock_data.empty:
                        symbol = base_symbol
            
            if not stock_data.empty:
                data[symbol] = stock_data
                logger.info(f"Fetched data for {symbol}")
            else:
                logger.error(f"No data available for {symbol} (all formats and periods tried)")
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")

    return data

if __name__ == "__main__":
    # Test the function
    symbols = get_nifty50_symbols()
    print(f"Nifty 50 Symbols: {symbols}")
    print(f"Total symbols: {len(symbols)}")
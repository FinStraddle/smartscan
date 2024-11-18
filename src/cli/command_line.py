import argparse
import logging
import os
from datetime import datetime
from src.data_collection.stock_data import StockDataCollector
from src.data_processing.data_processor import process_stock_data
from src.analysis.technical_indicators import calculate_technical_indicators, generate_signals
from src.output.report_generator import generate_analysis_report

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def format_price(price):
    return f"₹{price:,.2f}"

def print_stock_analysis(symbol, df, signal):
    """Print detailed analysis for a stock"""
    current_price = df['Close'].iloc[-1]
    prev_close = df['Close'].iloc[-2]
    price_change = ((current_price - prev_close) / prev_close) * 100
    
    # Format indicators
    rsi = df['RSI'].iloc[-1]
    macd = df['MACD'].iloc[-1]
    signal_strength = df['Signal_Strength'].iloc[-1]
    
    # Volume analysis
    vol_ratio = df['Volume_Ratio'].iloc[-1]
    vol_trend = "High" if vol_ratio > 1.5 else "Low" if vol_ratio < 0.5 else "Normal"
    
    # Price vs Moving Averages
    sma_20 = df['SMA_20'].iloc[-1]
    sma_50 = df['SMA_50'].iloc[-1]
    
    # Format output
    logger.info(f"\n{'='*50}")
    logger.info(f"Stock Analysis: {symbol}")
    logger.info(f"{'='*50}")
    logger.info(f"Signal: {signal}")
    logger.info(f"Current Price: {format_price(current_price)} ({price_change:+.2f}%)")
    logger.info(f"\nKey Indicators:")
    logger.info(f"RSI: {rsi:.2f}")
    logger.info(f"MACD: {macd:.3f}")
    logger.info(f"Signal Strength: {signal_strength:.2f}")
    logger.info(f"\nMoving Averages:")
    logger.info(f"SMA20: {format_price(sma_20)}")
    logger.info(f"SMA50: {format_price(sma_50)}")
    logger.info(f"\nVolume Analysis:")
    logger.info(f"Volume Trend: {vol_trend} (Ratio: {vol_ratio:.2f})")
    logger.info(f"{'='*50}\n")

def run_cli():
    parser = argparse.ArgumentParser(description="SmartScan - NSE Market Scanner")
    parser.add_argument("--period", type=str, default="1y", 
                      help="Data fetch period (e.g., 1d, 1mo, 1y)")
    parser.add_argument("--min-strength", type=float, default=1.0,
                      help="Minimum signal strength to display (default: 1.0)")
    parser.add_argument("--save-report", action="store_true",
                      help="Save analysis report to file")
    args = parser.parse_args()

    # Print header
    logger.info("\n" + "="*60)
    logger.info(f"SmartScan - NSE Market Scanner ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    logger.info("="*60 + "\n")

    # Initialize data collector
    collector = StockDataCollector()

    # Define Nifty 50 symbols with index
    nifty50_symbols = [
        "^NSEI",  # Nifty 50 Index
        "ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS",
        "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BPCL.NS", "BHARTIARTL.NS",
        "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DIVISLAB.NS", "DRREDDY.NS",
        "EICHERMOT.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS",
        "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "ITC.NS",
        "INDUSINDBK.NS", "INFY.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LT.NS",
        "M&M.NS", "MARUTI.NS", "NTPC.NS", "NESTLEIND.NS", "ONGC.NS",
        "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SBIN.NS", "SUNPHARMA.NS",
        "TCS.NS", "TATACONSUM.NS", "TATAMOTORS.NS", "TATASTEEL.NS", "TECHM.NS",
        "TITAN.NS", "UPL.NS", "ULTRACEMCO.NS", "WIPRO.NS"
    ]

    # Fetch and process data
    logger.info("Fetching Nifty 50 data...")
    data = collector.get_multiple_stock_data(nifty50_symbols, period=args.period)
    if not data:
        logger.error("No data fetched. Exiting...")
        return

    logger.info("Processing data...")
    processed_data = process_stock_data(data)

    logger.info("Calculating technical indicators...")
    analyzed_data = calculate_technical_indicators(processed_data)

    logger.info("Generating signals...")
    signals = generate_signals(analyzed_data)

    # Generate and save report if requested
    if args.save_report:
        report_path = generate_analysis_report(analyzed_data, signals)
        if report_path:
            logger.info(f"\nAnalysis report saved to: {report_path}")
            # Ensure the file extension is .md
            if not report_path.endswith('.md'):
                new_path = report_path.rsplit('.', 1)[0] + '.md'
                os.rename(report_path, new_path)
                logger.info(f"Report renamed to: {new_path}")

    # Organize stocks by signal type
    signal_groups = {
        'Strong Buy': [], 'Buy': [], 'Sell': [], 'Strong Sell': []
    }
    
    for symbol, df in signals.items():
        if df is not None and not df.empty:
            signal = df['Signal'].iloc[-1]
            strength = abs(df['Signal_Strength'].iloc[-1])
            
            if signal != 'Hold' and strength >= args.min_strength:
                signal_groups[signal].append((symbol, df))

    # Print analysis for each group
    for signal_type, stocks in signal_groups.items():
        if stocks:
            logger.info(f"\n{signal_type} Signals ({len(stocks)} stocks):")
            logger.info("="*60)
            for symbol, df in stocks:
                print_stock_analysis(symbol, df, signal_type)

    # Print distribution summary
    logger.info("\nSignal Distribution Summary")
    logger.info("="*60)
    for signal_type, stocks in signal_groups.items():
        logger.info(f"{signal_type:<12}: {len(stocks):>3} stocks")
    
    total_analyzed = sum(len(stocks) for stocks in signal_groups.values())
    logger.info(f"\nTotal Actionable Signals: {total_analyzed} stocks")
    logger.info("="*60 + "\n")

if __name__ == "__main__":
    run_cli()
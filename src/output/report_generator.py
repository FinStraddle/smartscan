import os
from datetime import datetime
import logging
from ..visualization.chart_generator import generate_stock_chart

logger = logging.getLogger(__name__)

def generate_analysis_report(analyzed_data, signals):
    """
    Generate a detailed analysis report and save it to a file
    :param analyzed_data: Dictionary of DataFrames with technical indicators
    :param signals: Dictionary of signal data for each stock
    :return: Path to the generated report file
    """
    try:
        # Create drafts directory if it doesn't exist
        drafts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'drafts')
        charts_dir = os.path.join(drafts_dir, 'charts')
        os.makedirs(drafts_dir, exist_ok=True)
        os.makedirs(charts_dir, exist_ok=True)
        
        # Generate filename with current date
        current_date = datetime.now().strftime('%Y-%m-%d')
        filename = f'nifty50_analysis-{current_date}.md'
        filepath = os.path.join(drafts_dir, filename)
        
        # Count signals
        buy_signals = 0
        sell_signals = 0
        strong_sell_signals = 0
        
        for symbol, df in signals.items():
            if df is not None and not df.empty and symbol != '^NSEI':
                signal = df['Signal'].iloc[-1]
                if signal in ['Strong Buy', 'Buy']:
                    buy_signals += 1
                elif signal == 'Sell':
                    sell_signals += 1
                elif signal == 'Strong Sell':
                    strong_sell_signals += 1
        
        report_content = ""
        
        # Write header
        report_content += "# Nifty 50 Technical Analysis Report\n\n"
        report_content += f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        
        # Add Nifty 50 Index Analysis if available
        if '^NSEI' in analyzed_data and '^NSEI' in signals:
            nifty_data = signals['^NSEI']
            if not nifty_data.empty:
                current_value = nifty_data['Close'].iloc[-1]
                prev_close = nifty_data['Close'].iloc[-2]
                change = ((current_value - prev_close) / prev_close) * 100
                signal = nifty_data['Signal'].iloc[-1]
                rsi = nifty_data['RSI'].iloc[-1]
                macd = nifty_data['MACD'].iloc[-1]
                signal_strength = nifty_data['Signal_Strength'].iloc[-1]
                
                report_content += "## Nifty 50 Index Overview\n\n"
                report_content += f"- Current Value: **{current_value:,.2f}** ({change:+.2f}%)\n"
                report_content += f"- Signal: **{signal}** (Strength: {signal_strength:.2f})\n"
                report_content += f"- RSI: {rsi:.2f}\n"
                report_content += f"- MACD: {macd:.3f}\n\n"
                
                # Generate and add index chart
                chart_path = generate_stock_chart(analyzed_data['^NSEI'], 'NIFTY50', charts_dir)
                relative_chart_path = os.path.relpath(chart_path, drafts_dir)
                report_content += f"![Nifty 50 Chart]({relative_chart_path})\n\n"
        
        # Write market summary
        report_content += "## Market Analysis Summary\n\n"
        report_content += f"- Strong Buy/Buy Signals: **{buy_signals} stocks**\n"
        report_content += f"- Sell Signals: **{sell_signals} stocks**\n"
        report_content += f"- Strong Sell Signals: **{strong_sell_signals} stocks**\n\n"
        
        # Add table header for two-column layout
        report_content += "## Detailed Stock Analysis\n\n"
        report_content += "| Stock Analysis | Technical Chart |\n"
        report_content += "|----------------|------------------|\n"
        
        # Process stocks by signal category
        categories = {
            'Buy Signals': ['Strong Buy', 'Buy'],
            'Sell Signals': ['Sell'],
            'Strong Sell Signals': ['Strong Sell']
        }
        
        for category, signal_types in categories.items():
            report_content += f"\n### {category}\n\n"
            
            for symbol, df in signals.items():
                if df is not None and not df.empty and symbol != '^NSEI':
                    signal = df['Signal'].iloc[-1]
                    if signal in signal_types:
                        # Generate chart
                        chart_path = generate_stock_chart(analyzed_data[symbol], symbol, charts_dir)
                        relative_chart_path = os.path.relpath(chart_path, drafts_dir)
                        
                        # Format stock info
                        current_price = df['Close'].iloc[-1]
                        prev_close = df['Close'].iloc[-2]
                        price_change = ((current_price - prev_close) / prev_close) * 100
                        rsi = df['RSI'].iloc[-1]
                        macd = df['MACD'].iloc[-1]
                        signal_strength = df['Signal_Strength'].iloc[-1]
                        sma_20 = df['SMA_20'].iloc[-1]
                        sma_50 = df['SMA_50'].iloc[-1]
                        vol_ratio = df['Volume_Ratio'].iloc[-1]
                        vol_trend = "High" if vol_ratio > 1.5 else "Low" if vol_ratio < 0.5 else "Normal"
                        
                        stock_info = (
                            f"**{symbol}**<br>\n"
                            f"Signal: {signal}<br>\n"
                            f"Price: ₹{current_price:,.2f} ({price_change:+.2f}%)<br>\n"
                            f"RSI: {rsi:.2f}<br>\n"
                            f"MACD: {macd:.3f}<br>\n"
                            f"Signal Strength: {signal_strength:.2f}<br>\n"
                            f"SMA20: ₹{sma_20:,.2f}<br>\n"
                            f"SMA50: ₹{sma_50:,.2f}<br>\n"
                            f"Volume: {vol_trend} ({vol_ratio:.2f}x)"
                        )
                        
                        # Add to table
                        report_content += f"| {stock_info} | ![{symbol} Chart]({relative_chart_path}) |\n"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"Analysis report generated successfully: {filepath}")
        return filepath
            
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        return None

import mplfinance as mpf
import pandas as pd
import os
import matplotlib.pyplot as plt

def generate_stock_chart(stock_data, symbol, output_dir):
    """
    Generate a technical analysis chart for a given stock.
    
    Args:
        stock_data (pd.DataFrame): OHLCV data with technical indicators
        symbol (str): Stock symbol
        output_dir (str): Directory to save the chart
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a copy of the data to avoid modifications to original
    df = stock_data.copy()
    
    # Convert index to datetime if not already
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    
    # Prepare additional plots
    additional_plots = []
    
    # Add RSI with reference lines
    if 'RSI' in df.columns:
        # Add RSI line
        additional_plots.append(
            mpf.make_addplot(df['RSI'], panel=2, ylabel='RSI',
                           color='purple', width=0.7)
        )
        # Add RSI reference lines (30 and 70)
        rsi_length = len(df)
        additional_plots.extend([
            mpf.make_addplot([30] * rsi_length, panel=2, color='gray', linestyle='--', alpha=0.3),
            mpf.make_addplot([70] * rsi_length, panel=2, color='gray', linestyle='--', alpha=0.3)
        ])
    
    # Add MACD
    if all(x in df.columns for x in ['MACD', 'MACD_Signal', 'MACD_Hist']):
        additional_plots.extend([
            mpf.make_addplot(df['MACD'], panel=3, color='blue', ylabel='MACD', width=0.7),
            mpf.make_addplot(df['MACD_Signal'], panel=3, color='orange', width=0.7),
            mpf.make_addplot(df['MACD_Hist'], type='bar', panel=3, color='dimgray', alpha=0.3, width=0.7)
        ])
    
    # Add Bollinger Bands
    if all(x in df.columns for x in ['BB_Upper', 'BB_Lower', 'BB_Mid']):
        additional_plots.extend([
            mpf.make_addplot(df['BB_Upper'], color='gray', alpha=0.3),
            mpf.make_addplot(df['BB_Lower'], color='gray', alpha=0.3),
            mpf.make_addplot(df['BB_Mid'], color='blue', alpha=0.3)
        ])
    
    # Add SMAs
    if 'SMA_20' in df.columns:
        additional_plots.append(
            mpf.make_addplot(df['SMA_20'], color='blue', width=0.7, alpha=0.7)
        )
    if 'SMA_50' in df.columns:
        additional_plots.append(
            mpf.make_addplot(df['SMA_50'], color='red', width=0.7, alpha=0.7)
        )

    # Custom style settings
    style = mpf.make_mpf_style(
        base_mpf_style='charles',
        gridstyle=':',
        y_on_right=False,
        gridcolor='gray',
        rc={
            'font.size': 8,
            'axes.titlesize': 10,
            'axes.labelsize': 8,
            'xtick.labelsize': 8,
            'ytick.labelsize': 8,
            'axes.linewidth': 0.5,
            'grid.linewidth': 0.5,
            'grid.alpha': 0.2,
        }
    )
    
    # Figure size and layout settings
    kwargs = dict(
        figsize=(12, 8),
        figratio=(16,9),
        panel_ratios=(6,2,2,2),  # Adjusted panel ratios
        type='candle',
        volume=True,
        addplot=additional_plots,
        style=style,
        title=f'\n{symbol} Technical Analysis\n',
        returnfig=True,
        tight_layout=True,
        volume_panel=1,
        scale_padding=0.2,
        scale_width_adjustment=dict(candle=0.8, volume=0.7),
    )
    
    # Create the chart
    fig, axes = mpf.plot(df, **kwargs)
    
    # Save the chart with high DPI for better quality
    output_file = os.path.join(output_dir, f'{symbol}_technical_analysis.png')
    plt.savefig(output_file, bbox_inches='tight', dpi=300, pad_inches=0.2)
    plt.close(fig)
    
    return output_file

import pandas as pd
import numpy as np
from ta import add_all_ta_features
from ta.trend import MACD, SMAIndicator, EMAIndicator, ADXIndicator, VortexIndicator
from ta.momentum import RSIIndicator, StochasticOscillator, TSIIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator, ChaikinMoneyFlowIndicator, EaseOfMovementIndicator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_custom_indicators(df):
    """Calculate custom technical indicators"""
    try:
        # Price-based indicators
        df['SMA_20'] = SMAIndicator(close=df['Close'], window=20).sma_indicator()
        df['SMA_50'] = SMAIndicator(close=df['Close'], window=50).sma_indicator()
        df['EMA_20'] = EMAIndicator(close=df['Close'], window=20).ema_indicator()
        df['EMA_50'] = EMAIndicator(close=df['Close'], window=50).ema_indicator()
        
        # Momentum indicators
        df['RSI'] = RSIIndicator(close=df['Close']).rsi()
        stoch = StochasticOscillator(high=df['High'], low=df['Low'], close=df['Close'])
        df['Stoch_K'] = stoch.stoch()
        df['Stoch_D'] = stoch.stoch_signal()
        df['TSI'] = TSIIndicator(close=df['Close']).tsi()
        
        # Trend indicators
        macd = MACD(close=df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        df['MACD_Hist'] = macd.macd_diff()
        
        # ADX for trend strength
        adx = ADXIndicator(high=df['High'], low=df['Low'], close=df['Close'])
        df['ADX'] = adx.adx()
        df['DI_plus'] = adx.adx_pos()
        df['DI_minus'] = adx.adx_neg()
        
        # Vortex Indicator
        vortex = VortexIndicator(high=df['High'], low=df['Low'], close=df['Close'])
        df['VI_plus'] = vortex.vortex_indicator_pos()
        df['VI_minus'] = vortex.vortex_indicator_neg()
        
        # Volatility indicators
        bb = BollingerBands(close=df['Close'])
        df['BB_Upper'] = bb.bollinger_hband()
        df['BB_Lower'] = bb.bollinger_lband()
        df['BB_Mid'] = bb.bollinger_mavg()
        df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Mid']
        
        # ATR for volatility
        atr = AverageTrueRange(high=df['High'], low=df['Low'], close=df['Close'])
        df['ATR'] = atr.average_true_range()
        
        # Volume indicators
        df['OBV'] = OnBalanceVolumeIndicator(close=df['Close'], volume=df['Volume']).on_balance_volume()
        df['CMF'] = ChaikinMoneyFlowIndicator(high=df['High'], low=df['Low'], close=df['Close'], volume=df['Volume']).chaikin_money_flow()
        df['EOM'] = EaseOfMovementIndicator(high=df['High'], low=df['Low'], volume=df['Volume']).ease_of_movement()
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_MA']
        
        # Support and Resistance levels
        df['Pivot'] = (df['High'] + df['Low'] + df['Close']) / 3
        df['R1'] = 2 * df['Pivot'] - df['Low']
        df['S1'] = 2 * df['Pivot'] - df['High']
        
        # Fibonacci Retracement levels
        high = df['High'].max()
        low = df['Low'].min()
        diff = high - low
        df['Fib_38.2'] = high - (0.382 * diff)
        df['Fib_50.0'] = high - (0.500 * diff)
        df['Fib_61.8'] = high - (0.618 * diff)
        
        # VWAP calculation
        df['VWAP'] = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()
        
        return df
    except Exception as e:
        logger.error(f"Error calculating custom indicators: {e}")
        return df

def get_signal_strength(row):
    """Calculate signal strength based on multiple indicators"""
    strength = 0
    
    # Trend strength (0-3 points)
    if row['Close'] > row['SMA_20'] and row['SMA_20'] > row['SMA_50']:
        strength += 1.5  # Strong uptrend
    elif row['Close'] < row['SMA_20'] and row['SMA_20'] < row['SMA_50']:
        strength -= 1.5  # Strong downtrend
    
    # ADX trend strength (0-2 points)
    if row['ADX'] > 25:
        if row['DI_plus'] > row['DI_minus']:
            strength += 1
        else:
            strength -= 1
    
    # RSI signals (0-2 points)
    if row['RSI'] < 30:
        strength += 1  # Oversold
    elif row['RSI'] > 70:
        strength -= 1  # Overbought
    
    # MACD signals (0-2 points)
    if row['MACD'] > row['MACD_Signal']:
        strength += 1
    else:
        strength -= 1
    
    # Vortex Indicator (0-1 point)
    if row['VI_plus'] > row['VI_minus']:
        strength += 0.5
    else:
        strength -= 0.5
    
    # Volume and Money Flow (0-1.5 points)
    if row['Volume_Ratio'] > 1.5 and row['CMF'] > 0:  # High volume with positive money flow
        strength = strength * 1.2 if strength > 0 else strength * 0.8
    
    # Support/Resistance confirmation
    if row['Close'] < row['S1']:  # Near support
        strength += 0.5
    elif row['Close'] > row['R1']:  # Near resistance
        strength -= 0.5
    
    # ATR volatility adjustment
    atr_ratio = row['ATR'] / row['Close']
    if atr_ratio > 0.02:  # High volatility
        strength = strength * 0.8  # Reduce confidence in signals during high volatility
        
    return strength

def calculate_technical_indicators(data):
    """
    Calculate technical indicators for the given stock data
    :param data: Dictionary of processed DataFrames with stock data
    :return: Dictionary of DataFrames with added technical indicators
    """
    analyzed_data = {}
    for symbol, df in data.items():
        try:
            if len(df) < 50:  # Need at least 50 data points for reliable indicators
                logger.warning(f"Insufficient data points for {symbol}. Skipping...")
                continue
            
            # Calculate custom indicators
            df = calculate_custom_indicators(df)
            
            # Add to analyzed data if successful
            analyzed_data[symbol] = df
            logger.info(f"Successfully calculated indicators for {symbol}")
            
        except Exception as e:
            logger.error(f"Error calculating indicators for {symbol}: {e}")
            continue

    return analyzed_data

def generate_signals(data):
    """
    Generate buy/sell signals based on technical indicators
    :param data: Dictionary of DataFrames with technical indicators
    :return: Dictionary of DataFrames with buy/sell signals
    """
    signals = {}
    for symbol, df in data.items():
        try:
            # Calculate signal strength
            df['Signal_Strength'] = df.apply(get_signal_strength, axis=1)
            
            # Generate signals based on strength
            conditions = {
                'Strong Buy': df['Signal_Strength'] > 2.5,
                'Buy': (df['Signal_Strength'] > 1) & (df['Signal_Strength'] <= 2.5),
                'Hold': (df['Signal_Strength'] >= -1) & (df['Signal_Strength'] <= 1),
                'Sell': (df['Signal_Strength'] < -1) & (df['Signal_Strength'] >= -2.5),
                'Strong Sell': df['Signal_Strength'] < -2.5
            }
            
            # Initialize signal column with 'Hold'
            df['Signal'] = 'Hold'
            
            # Apply conditions
            for signal, condition in conditions.items():
                df.loc[condition, 'Signal'] = signal
            
            # Add key indicator values for reference
            df['Signal_RSI'] = df['RSI'].round(2)
            df['Signal_MACD'] = df['MACD'].round(3)
            df['Signal_BB_Width'] = df['BB_Width'].round(3)
            
            signals[symbol] = df
            logger.info(f"Generated signals for {symbol}")
            
        except Exception as e:
            logger.error(f"Error generating signals for {symbol}: {e}")
            continue

    return signals
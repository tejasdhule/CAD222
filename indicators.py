import pandas as pd
import numpy as np
from config import MACD_FAST, MACD_SLOW, MACD_SIGNAL, RSI_PERIOD, MFI_PERIOD, VOLUME_MA_SHORT, VOLUME_MA_LONG

def calculate_macd(df):
    """Calculate MACD indicator using pure pandas"""
    try:
        close = df['Close']
        
        # Calculate EMAs
        ema_fast = close.ewm(span=MACD_FAST).mean()
        ema_slow = close.ewm(span=MACD_SLOW).mean()
        
        # MACD line
        macd_line = ema_fast - ema_slow
        
        # Signal line (EMA of MACD)
        signal_line = macd_line.ewm(span=MACD_SIGNAL).mean()
        
        # Histogram
        histogram = macd_line - signal_line
        
        df['MACD'] = macd_line
        df['MACD_Signal'] = signal_line
        df['MACD_Histogram'] = histogram
        
        # Calculate crossover signals
        df['MACD_Crossover'] = np.where(
            (df['MACD'] > df['MACD_Signal']) & 
            (df['MACD'].shift(1) <= df['MACD_Signal'].shift(1)), 
            1, 0
        )
        
        return df
    except Exception as e:
        print(f"Error calculating MACD: {str(e)}")
        return df

def calculate_rsi(df):
    """Calculate RSI indicator using pure pandas"""
    try:
        close = df['Close']
        delta = close.diff()
        
        # Separate gains and losses
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # Calculate average gains and losses
        avg_gain = gain.rolling(window=RSI_PERIOD).mean()
        avg_loss = loss.rolling(window=RSI_PERIOD).mean()
        
        # Calculate RS and RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        df['RSI'] = rsi
        
        # RSI signals
        df['RSI_Oversold'] = np.where(df['RSI'] < 30, 1, 0)
        df['RSI_Overbought'] = np.where(df['RSI'] > 70, 1, 0)
        
        return df
    except Exception as e:
        print(f"Error calculating RSI: {str(e)}")
        return df

def calculate_mfi(df):
    """Calculate Money Flow Index"""
    try:
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        money_flow = typical_price * df['Volume']
        
        # Positive and negative money flow
        positive_flow = money_flow.where(typical_price > typical_price.shift(1), 0)
        negative_flow = money_flow.where(typical_price < typical_price.shift(1), 0)
        
        # Calculate MFI
        positive_mf = positive_flow.rolling(window=MFI_PERIOD).sum()
        negative_mf = negative_flow.rolling(window=MFI_PERIOD).sum()
        
        mfr = positive_mf / negative_mf
        mfi = 100 - (100 / (1 + mfr))
        
        df['MFI'] = mfi
        
        # MFI signals
        df['MFI_Oversold'] = np.where(df['MFI'] < 20, 1, 0)
        df['MFI_Overbought'] = np.where(df['MFI'] > 80, 1, 0)
        
        return df
    except Exception as e:
        print(f"Error calculating MFI: {str(e)}")
        return df

def calculate_volume_indicators(df):
    """Calculate volume-based indicators"""
    try:
        # Volume moving averages
        df['Volume_MA_Short'] = df['Volume'].rolling(window=VOLUME_MA_SHORT).mean()
        df['Volume_MA_Long'] = df['Volume'].rolling(window=VOLUME_MA_LONG).mean()
        
        # Volume ratio
        df['Volume_Ratio'] = df['Volume'] / df['Volume_MA_Short']
        
        # Volume surge signal
        df['Volume_Surge'] = np.where(df['Volume_Ratio'] > 2.0, 1, 0)
        
        return df
    except Exception as e:
        print(f"Error calculating volume indicators: {str(e)}")
        return df

def calculate_all_indicators(df):
    """Calculate all technical indicators"""
    if df.empty:
        return df
    
    df = calculate_macd(df)
    df = calculate_rsi(df)
    df = calculate_mfi(df)
    df = calculate_volume_indicators(df)
    
    return df

def detect_crossover_signals(df):
    """Detect all crossover signals"""
    signals = []
    
    if df.empty:
        return signals
    
    latest = df.iloc[-1]
    
    # MACD crossover
    if latest['MACD_Crossover'] == 1:
        signals.append({
            'type': 'MACD_Bullish',
            'message': 'MACD bullish crossover detected',
            'strength': 'Medium'
        })
    
    # RSI signals
    if latest['RSI_Oversold'] == 1:
        signals.append({
            'type': 'RSI_Oversold',
            'message': f'RSI oversold: {latest["RSI"]:.2f}',
            'strength': 'High'
        })
    
    if latest['RSI_Overbought'] == 1:
        signals.append({
            'type': 'RSI_Overbought',
            'message': f'RSI overbought: {latest["RSI"]:.2f}',
            'strength': 'High'
        })
    
    # MFI signals
    if latest['MFI_Oversold'] == 1:
        signals.append({
            'type': 'MFI_Oversold',
            'message': f'MFI oversold: {latest["MFI"]:.2f}',
            'strength': 'Medium'
        })
    
    # Volume surge
    if latest['Volume_Surge'] == 1:
        signals.append({
            'type': 'Volume_Surge',
            'message': f'Volume surge: {latest["Volume_Ratio"]:.2f}x average',
            'strength': 'Medium'
        })
    
    return signals

def get_latest_signals(symbol, df):
    """Get latest signals for a stock"""
    signals = detect_crossover_signals(df)
    return {
        'symbol': symbol,
        'signals': signals,
        'timestamp': pd.Timestamp.now()
    }

def get_indicator_summary(df):
    """Get summary of all indicators"""
    if df.empty:
        return {}
    
    latest = df.iloc[-1]
    
    return {
        'MACD': {
            'value': latest.get('MACD', 0),
            'signal': latest.get('MACD_Signal', 0),
            'histogram': latest.get('MACD_Histogram', 0)
        },
        'RSI': {
            'value': latest.get('RSI', 50),
            'oversold': latest.get('RSI_Oversold', 0),
            'overbought': latest.get('RSI_Overbought', 0)
        },
        'MFI': {
            'value': latest.get('MFI', 50),
            'oversold': latest.get('MFI_Oversold', 0),
            'overbought': latest.get('MFI_Overbought', 0)
        },
        'Volume': {
            'current': latest.get('Volume', 0),
            'ratio': latest.get('Volume_Ratio', 1),
            'surge': latest.get('Volume_Surge', 0)
        }
    }
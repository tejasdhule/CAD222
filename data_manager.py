import yfinance as yf
import pandas as pd
import streamlit as st
import time
from datetime import datetime, timedelta
from config import NIFTY_100_SYMBOLS, HISTORICAL_PERIOD, REQUEST_DELAY, BATCH_SIZE
from utils import save_stock_data, load_stock_data, rate_limit_delay, create_data_folder
from indicators import calculate_all_indicators

class DataManager:
    def __init__(self):
        create_data_folder()
        self.last_update = {}
        
    def download_historical_data(self, symbol, progress_callback=None):
        """Download historical data for a single stock"""
        try:
            # Rate limiting
            rate_limit_delay()
            
            # Download data
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=HISTORICAL_PERIOD, interval="1h")
            
            if df.empty:
                st.warning(f"No data available for {symbol}")
                return False
            
            # Resample to 4-hour data
            df_4h = df.resample('4h').agg({
                'Open': 'first',
                'High': 'max',
                'Low': 'min',
                'Close': 'last',
                'Volume': 'sum'
            }).dropna()
            
            # Calculate indicators
            df_4h = calculate_all_indicators(df_4h)
            
            # Save data
            success = save_stock_data(symbol, df_4h)
            
            if success:
                self.last_update[symbol] = datetime.now()
                if progress_callback:
                    progress_callback(symbol, True)
                return True
            else:
                if progress_callback:
                    progress_callback(symbol, False)
                return False
                
        except Exception as e:
            st.error(f"Error downloading {symbol}: {str(e)}")
            if progress_callback:
                progress_callback(symbol, False)
            return False
    
    def download_batch_data(self, symbols, progress_bar=None, status_text=None):
        """Download data for multiple stocks in batches"""
        total_symbols = len(symbols)
        successful_downloads = 0
        failed_downloads = []
        
        def update_progress(symbol, success):
            nonlocal successful_downloads
            if success:
                successful_downloads += 1
            else:
                failed_downloads.append(symbol)
            
            if progress_bar:
                progress_bar.progress(successful_downloads / total_symbols)
            
            if status_text:
                status_text.text(f"Downloaded: {successful_downloads}/{total_symbols} | Failed: {len(failed_downloads)}")
        
        # Process in batches
        for i in range(0, len(symbols), BATCH_SIZE):
            batch = symbols[i:i + BATCH_SIZE]
            
            for symbol in batch:
                self.download_historical_data(symbol, update_progress)
        
        return {
            'successful': successful_downloads,
            'failed': failed_downloads,
            'total': total_symbols
        }
    
    def get_stock_data(self, symbol):
        """Get stock data from cache or download if needed"""
        df = load_stock_data(symbol)
        
        if df.empty:
            # Try to download data
            if self.download_historical_data(symbol):
                df = load_stock_data(symbol)
        
        return df
    
    def is_data_stale(self, symbol, hours=4):
        """Check if data is stale and needs updating"""
        if symbol not in self.last_update:
            return True
        
        time_diff = datetime.now() - self.last_update[symbol]
        return time_diff > timedelta(hours=hours)
    
    def refresh_symbol_data(self, symbol):
        """Refresh data for a specific symbol"""
        return self.download_historical_data(symbol)
    
    def get_data_status(self, symbols):
        """Get status of data for multiple symbols"""
        status = {
            'loaded': [],
            'missing': [],
            'stale': []
        }
        
        for symbol in symbols:
            df = load_stock_data(symbol)
            
            if df.empty:
                status['missing'].append(symbol)
            elif self.is_data_stale(symbol):
                status['stale'].append(symbol)
            else:
                status['loaded'].append(symbol)
        
        return status
    
    def get_latest_prices(self, symbols):
        """Get latest prices for multiple symbols"""
        prices = {}
        
        for symbol in symbols:
            df = load_stock_data(symbol)
            if not df.empty:
                latest = df.iloc[-1]
                prices[symbol] = {
                    'price': latest['Close'],
                    'change': latest['Close'] - latest['Open'],
                    'change_pct': ((latest['Close'] - latest['Open']) / latest['Open']) * 100,
                    'timestamp': df.index[-1]
                }
        
        return prices
    
    def cleanup_old_data(self, days=30):
        """Clean up data files older than specified days"""
        import os
        import glob
        
        cutoff_date = datetime.now() - timedelta(days=days)
        data_files = glob.glob("stock_data/historical/*.csv")
        
        cleaned_files = 0
        for file_path in data_files:
            try:
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_time < cutoff_date:
                    os.remove(file_path)
                    cleaned_files += 1
            except Exception as e:
                st.warning(f"Error cleaning file {file_path}: {str(e)}")
        
        return cleaned_files
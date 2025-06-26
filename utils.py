import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time
import streamlit as st

def create_data_folder():
    """Create data folder if it doesn't exist"""
    if not os.path.exists("stock_data"):
        os.makedirs("stock_data")
    if not os.path.exists("stock_data/historical"):
        os.makedirs("stock_data/historical")
    if not os.path.exists("stock_data/alerts"):
        os.makedirs("stock_data/alerts")

def get_file_path(symbol, data_type="historical"):
    """Get file path for stock data"""
    return f"stock_data/{data_type}/{symbol.replace('.NS', '')}.csv"

def load_stock_data(symbol):
    """Load stock data from CSV file"""
    file_path = get_file_path(symbol)
    try:
        if os.path.exists(file_path):
            df = pd.read_csv(file_path, index_col=0, parse_dates=True)
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data for {symbol}: {str(e)}")
        return pd.DataFrame()

def save_stock_data(symbol, df):
    """Save stock data to CSV file"""
    file_path = get_file_path(symbol)
    try:
        df.to_csv(file_path)
        return True
    except Exception as e:
        st.error(f"Error saving data for {symbol}: {str(e)}")
        return False

def load_alert_log():
    """Load alert log from JSON file"""
    log_file = "stock_data/alerts/alert_log.json"
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        st.error(f"Error loading alert log: {str(e)}")
        return {}

def save_alert_log(alert_log):
    """Save alert log to JSON file"""
    log_file = "stock_data/alerts/alert_log.json"
    try:
        with open(log_file, 'w') as f:
            json.dump(alert_log, f, indent=2, default=str)
        return True
    except Exception as e:
        st.error(f"Error saving alert log: {str(e)}")
        return False

def rate_limit_delay():
    """Add delay for API rate limiting"""
    from config import REQUEST_DELAY
    time.sleep(REQUEST_DELAY)

def format_number(number):
    """Format number with proper suffix"""
    if number >= 1e9:
        return f"{number/1e9:.2f}B"
    elif number >= 1e6:
        return f"{number/1e6:.2f}M"
    elif number >= 1e3:
        return f"{number/1e3:.2f}K"
    else:
        return f"{number:.2f}"

def format_percentage(value):
    """Format percentage with color"""
    color = "green" if value >= 0 else "red"
    sign = "+" if value >= 0 else ""
    return f"<span style='color: {color}'>{sign}{value:.2f}%</span>"

def get_color_for_value(value, threshold=0):
    """Get color based on value relative to threshold"""
    return "green" if value >= threshold else "red"

def validate_email_config():
    """Validate email configuration"""
    from config import EMAIL_USER, EMAIL_PASSWORD, EMAIL_RECIPIENTS
    return bool(EMAIL_USER and EMAIL_PASSWORD and EMAIL_RECIPIENTS)

def get_stock_status_summary(symbols):
    """Get summary of stock statuses"""
    status_counts = {"loaded": 0, "missing": 0, "error": 0}
    
    for symbol in symbols:
        try:
            df = load_stock_data(symbol)
            if not df.empty:
                status_counts["loaded"] += 1
            else:
                status_counts["missing"] += 1
        except:
            status_counts["error"] += 1
    
    return status_counts

def clean_old_alerts(days=7):
    """Clean alert log entries older than specified days"""
    alert_log = load_alert_log()
    cutoff_date = datetime.now() - timedelta(days=days)
    
    cleaned_log = {}
    for symbol, alerts in alert_log.items():
        cleaned_alerts = []
        for alert in alerts:
            try:
                alert_date = datetime.fromisoformat(alert.get('timestamp', ''))
                if alert_date >= cutoff_date:
                    cleaned_alerts.append(alert)
            except:
                continue
        if cleaned_alerts:
            cleaned_log[symbol] = cleaned_alerts
    
    save_alert_log(cleaned_log)
    return len(alert_log) - len(cleaned_log)
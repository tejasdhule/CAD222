import smtplib
import pandas as pd
from datetime import datetime
import streamlit as st
from config import EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD, EMAIL_RECIPIENTS
from utils import load_alert_log, save_alert_log
from indicators import detect_crossover_signals, get_latest_signals

class AlertSystem:
    def __init__(self):
        self.alert_log = load_alert_log()
        
    def send_email_alert(self, subject, message):
        """Send email alert"""
        try:
            if not EMAIL_USER or not EMAIL_PASSWORD:
                st.warning("Email credentials not configured")
                return False
            
            if not EMAIL_RECIPIENTS:
                st.warning("No email recipients configured")
                return False
            
            # Simple email format without MIME
            email_message = f"Subject: {subject}\nFrom: {EMAIL_USER}\nTo: {', '.join(EMAIL_RECIPIENTS)}\nContent-Type: text/html\n\n{message}"
            
            server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            
            server.sendmail(EMAIL_USER, EMAIL_RECIPIENTS, email_message)
            server.quit()
            
            return True
            
        except Exception as e:
            st.error(f"Failed to send email: {str(e)}")
            return False
    
    def create_alert_message(self, symbol, signals, stock_data):
        """Create formatted alert message"""
        if stock_data.empty:
            return None
        
        latest = stock_data.iloc[-1]
        
        message = f"""
        <html>
        <body>
        <h2>🚨 Stock Alert: {symbol.replace('.NS', '')}</h2>
        <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Current Price:</strong> ₹{latest['Close']:.2f}</p>
        
        <h3>Signals Detected:</h3>
        <ul>
        """
        
        for signal in signals:
            message += f"<li><strong>{signal['type']}:</strong> {signal['message']} (Strength: {signal['strength']})</li>"
        
        message += """
        </ul>
        
        <h3>Technical Indicators:</h3>
        <table border="1" style="border-collapse: collapse;">
        <tr>
            <td><strong>MACD:</strong></td>
            <td>{:.4f}</td>
        </tr>
        <tr>
            <td><strong>RSI:</strong></td>
            <td>{:.2f}</td>
        </tr>
        <tr>
            <td><strong>MFI:</strong></td>
            <td>{:.2f}</td>
        </tr>
        <tr>
            <td><strong>Volume Ratio:</strong></td>
            <td>{:.2f}x</td>
        </tr>
        </table>
        
        <p><em>This is an automated alert from your Nifty 100 Stock Analysis Dashboard.</em></p>
        </body>
        </html>
        """.format(
            latest.get('MACD', 0),
            latest.get('RSI', 50),
            latest.get('MFI', 50),
            latest.get('Volume_Ratio', 1)
        )
        
        return message
    
    def check_and_send_alerts(self, symbol, stock_data):
        """Check for signals and send alerts if needed"""
        if stock_data.empty:
            return False
        
        signals = detect_crossover_signals(stock_data)
        
        if not signals:
            return False
        
        # Check if we've already sent an alert for this symbol today
        today = datetime.now().strftime('%Y-%m-%d')
        symbol_alerts = self.alert_log.get(symbol, [])
        
        # Check if any alert was sent today
        today_alerts = [alert for alert in symbol_alerts if alert.get('date', '') == today]
        
        if today_alerts:
            return False  # Already sent alert today
        
        # Create and send alert
        subject = f"Stock Alert: {symbol.replace('.NS', '')} - {len(signals)} Signal(s)"
        message = self.create_alert_message(symbol, signals, stock_data)
        
        if self.send_email_alert(subject, message):
            # Log the alert
            alert_entry = {
                'date': today,
                'timestamp': datetime.now().isoformat(),
                'signals': signals,
                'price': float(stock_data.iloc[-1]['Close'])
            }
            
            if symbol not in self.alert_log:
                self.alert_log[symbol] = []
            
            self.alert_log[symbol].append(alert_entry)
            save_alert_log(self.alert_log)
            
            return True
        
        return False
    
    def get_alert_summary(self):
        """Get summary of recent alerts"""
        summary = {
            'total_alerts': 0,
            'today_alerts': 0,
            'symbols_with_alerts': set()
        }
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        for symbol, alerts in self.alert_log.items():
            summary['total_alerts'] += len(alerts)
            summary['symbols_with_alerts'].add(symbol)
            
            today_alerts = [alert for alert in alerts if alert.get('date', '') == today]
            summary['today_alerts'] += len(today_alerts)
        
        summary['symbols_with_alerts'] = len(summary['symbols_with_alerts'])
        
        return summary
    
    def clear_old_alerts(self, days=30):
        """Clear alerts older than specified days"""
        cutoff_date = datetime.now() - pd.Timedelta(days=days)
        
        for symbol in list(self.alert_log.keys()):
            filtered_alerts = []
            for alert in self.alert_log[symbol]:
                try:
                    alert_date = datetime.fromisoformat(alert['timestamp'])
                    if alert_date >= cutoff_date:
                        filtered_alerts.append(alert)
                except:
                    continue
            
            if filtered_alerts:
                self.alert_log[symbol] = filtered_alerts
            else:
                del self.alert_log[symbol]
        
        save_alert_log(self.alert_log)
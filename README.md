# Nifty 100 Stock Analysis Dashboard

A comprehensive technical analysis dashboard built with Streamlit for analyzing Nifty 100 stocks with modern UI and automated alerts.

## Features

### 📊 Core Analysis
- **Real-time Data**: Live stock data from Yahoo Finance for all Nifty 100 stocks
- **Technical Indicators**: MACD, RSI, MFI with crossover detection
- **Volume Analysis**: Volume surge detection and ratio calculations
- **4-Hour Timeframe**: Optimized for intraday technical analysis

### 🎯 Signal Detection
- **Automated Scanner**: Scans all 100 stocks for trading signals
- **Signal Strength**: Classified as High, Medium, or Low strength
- **Crossover Alerts**: MACD bullish crossovers, RSI oversold/overbought conditions
- **Volume Surge**: Detects unusual volume activity

### 🔔 Alert System
- **Email Notifications**: HTML-formatted email alerts for trading signals
- **Daily Frequency Control**: Prevents spam with once-per-day alerts per stock
- **Alert History**: Maintains log of all sent alerts with timestamps

### 🎨 Modern UI
- **Gradient Headers**: Professional design with custom color schemes
- **Interactive Cards**: Hover effects and status badges for metrics
- **Progress Indicators**: Visual data coverage and loading states
- **Responsive Layout**: Works on desktop and mobile devices

## Installation

### Requirements
- Python 3.11+
- Dependencies listed in `pyproject.toml`

### Setup
1. Clone or extract the project files
2. Install dependencies:
   ```bash
   pip install streamlit yfinance plotly pandas numpy
   ```
3. Configure Streamlit:
   ```bash
   mkdir .streamlit
   # Copy the provided config.toml to .streamlit/
   ```

### Email Configuration (Optional)
Set environment variables for email alerts:
```bash
export EMAIL_USER="your-email@gmail.com"
export EMAIL_PASSWORD="your-app-password"
export EMAIL_RECIPIENTS="recipient1@example.com,recipient2@example.com"
```

## Usage

### Running the Dashboard
```bash
streamlit run app.py --server.port 5000
```

### Key Features
1. **Download Data**: Click "Download All Data" to fetch historical data for all stocks
2. **Select Stock**: Choose any Nifty 100 stock for detailed analysis
3. **View Charts**: Interactive candlestick charts with technical indicators
4. **Scan Signals**: Run signal scanner to find trading opportunities
5. **Set Alerts**: Configure email alerts for automated notifications

## Architecture

### Core Components
- `app.py`: Main Streamlit application with modern UI
- `data_manager.py`: Handles batch data downloading and caching
- `indicators.py`: Technical indicator calculations and signal detection
- `alert_system.py`: Email notification system with HTML formatting
- `config.py`: Configuration for stocks, indicators, and parameters
- `utils.py`: Utility functions for data handling and formatting

### Data Flow
1. **Data Collection**: Yahoo Finance API → 1-hour data → 4-hour resampling
2. **Indicator Calculation**: OHLCV data → Technical indicators → Signal detection
3. **Alert Processing**: Signals → Email formatting → SMTP delivery
4. **UI Rendering**: Processed data → Interactive charts → Modern dashboard

## Configuration

### Stock Symbols
Currently configured for 25 major Nifty 100 stocks. Expand the `NIFTY_100_SYMBOLS` list in `config.py` to include all 100 stocks.

### Technical Parameters
- MACD: 12, 26, 9 periods
- RSI: 14 periods (oversold <30, overbought >70)
- MFI: 14 periods (oversold <20, overbought >80)
- Volume: 20 and 50 period moving averages

### Performance Settings
- Request delay: 0.5 seconds between API calls
- Batch size: 10 stocks per batch
- Cache TTL: 4 hours for data staleness detection

## Troubleshooting

### Common Issues
1. **No Data Available**: Click "Download All Data" to fetch historical data
2. **Email Not Working**: Verify environment variables and Gmail app passwords
3. **Slow Loading**: Reduce batch size in `config.py` or increase request delay

### Data Storage
- Historical data stored in `stock_data/historical/` as CSV files
- Alert logs stored in `stock_data/alerts/alert_log.json`
- Automatic cleanup of old data after 30 days

## License

This project is for educational purposes only. Not financial advice.

## Support

For issues or questions about the dashboard functionality, check the configuration files and ensure all dependencies are properly installed.
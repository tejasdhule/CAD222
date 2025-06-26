# Nifty 100 Stock Analysis Dashboard

## Overview

This is a comprehensive technical analysis dashboard built with Streamlit that provides advanced stock analysis for Nifty 100 stocks. The application features modular architecture with automated signal detection, email alerts, and sophisticated technical indicators including MACD, RSI, and MFI analysis.

## System Architecture

The application follows a modular, object-oriented architecture with clear separation of concerns:

- **Frontend**: Streamlit-based web interface with multi-panel layouts
- **Data Layer**: DataManager class for batch downloading and caching stock data
- **Analysis Engine**: Technical indicators calculation with crossover detection
- **Alert System**: Email-based notification system for trading signals
- **Data Storage**: Local CSV files with organized folder structure

## Key Components

### Core Application (`app.py`)
- Main Streamlit application with comprehensive dashboard interface
- Modular design with separate functions for charting, scanning, and analysis
- Real-time signal detection and automated alert capabilities
- Multi-panel technical analysis with MACD, RSI, MFI indicators

### Data Management (`data_manager.py`)
- DataManager class for batch downloading and caching stock data
- Rate-limited API calls with progress tracking
- 4-hour timeframe resampling from hourly data
- Local CSV storage with organized folder structure

### Technical Analysis (`indicators.py`)
- Pure pandas implementation of technical indicators
- MACD, RSI, MFI calculations with crossover detection
- Volume analysis with surge detection
- Signal strength classification system

### Alert System (`alert_system.py`)
- Email-based notification system for trading signals
- HTML-formatted alert messages with technical data
- Daily alert frequency control to prevent spam
- Alert logging and history management

### Configuration (`config.py`)
- Nifty 100 stock symbols configuration
- Technical indicator parameters (periods, thresholds)
- Email and API rate limiting settings
- Environment variable management

### Utilities (`utils.py`)
- File management for data storage and retrieval
- Number formatting and percentage calculations
- Data validation and status checking functions
- Alert log maintenance and cleanup routines

### Dependencies
- **Streamlit**: Web application framework for interactive dashboards
- **yfinance**: Yahoo Finance API wrapper for Indian stock data
- **Plotly**: Advanced charting with subplot capabilities
- **Pandas**: Time series analysis and data manipulation
- **NumPy**: Numerical computations for technical indicators

## Data Flow

1. **User Input**: User selects stock symbols through sidebar interface
2. **Data Fetching**: Application queries Yahoo Finance API via yfinance
3. **Data Processing**: Raw stock data is processed using pandas/numpy
4. **Visualization**: Processed data is rendered using Plotly charts
5. **Real-time Updates**: Dashboard can refresh data for live monitoring

## External Dependencies

### Primary Services
- **Yahoo Finance API**: Source for real-time and historical stock data
- **Streamlit Cloud**: Hosting and deployment platform

### Python Libraries
- Data processing: pandas, numpy
- Visualization: plotly, streamlit
- Web scraping: beautifulsoup4 (yfinance dependency)
- Additional utilities: attrs, blinker, altair

## Deployment Strategy

- **Platform**: Streamlit Cloud with autoscale deployment
- **Runtime**: Python 3.11+ environment
- **Port Configuration**: Application runs on port 5000
- **Auto-deployment**: Configured for automatic deployment from repository
- **Scaling**: Autoscale deployment target for handling variable traffic

### Deployment Configuration
- Uses Nix package manager for reproducible environments
- Streamlit server configured for headless operation
- Light theme configuration for consistent UI appearance

## Changelog

- June 26, 2025: Fixed Python 3.13 compatibility issues by switching to Python 3.11
- June 26, 2025: Updated dependencies to resolve pandas compilation errors
- June 26, 2025: Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.subplots as sp
from datetime import datetime, timedelta
import time
import threading
from config import NIFTY_100_SYMBOLS, REFRESH_INTERVAL, MAX_CHARTS_PER_PAGE
from data_manager import DataManager
from alert_system import AlertSystem
from indicators import get_latest_signals, get_indicator_summary
from utils import (
    load_stock_data, format_number, format_percentage, get_color_for_value,
    validate_email_config, get_stock_status_summary, clean_old_alerts
)

# Page configuration
st.set_page_config(
    page_title="Nifty 100 Stock Analysis Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #1f77b4;
        --secondary-color: #ff7f0e;
        --success-color: #2ca02c;
        --danger-color: #d62728;
        --warning-color: #ff9800;
        --info-color: #17a2b8;
        --dark-color: #343a40;
        --light-color: #f8f9fa;
        --background-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Header styling */
    .main-header {
        background: var(--background-gradient);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        margin: 0;
    }
    
    /* Card styling */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 4px solid var(--primary-color);
        margin-bottom: 1rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .metric-card h3 {
        color: var(--dark-color);
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary-color);
        margin-bottom: 0.25rem;
    }
    
    .metric-delta {
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .metric-delta.positive {
        color: var(--success-color);
    }
    
    .metric-delta.negative {
        color: var(--danger-color);
    }
    
    /* Status indicators */
    .status-badge {
        display: inline-block;
        padding: 0.35rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-badge.success {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .status-badge.warning {
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffeaa7;
    }
    
    .status-badge.danger {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    
    .status-badge.info {
        background-color: #d1ecf1;
        color: #0c5460;
        border: 1px solid #bee5eb;
    }
    
    /* Sidebar styling */
    .sidebar-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 3px solid var(--primary-color);
    }
    
    /* Signal cards */
    .signal-card {
        background: linear-gradient(45deg, #667eea, #764ba2);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 0.8rem;
        color: white;
    }
    
    .signal-card.bullish {
        background: linear-gradient(45deg, #56ab2f, #a8e6cf);
        color: #1a5c1a;
    }
    
    .signal-card.bearish {
        background: linear-gradient(45deg, #ff4757, #ff6b7d);
        color: white;
    }
    
    .signal-card.neutral {
        background: linear-gradient(45deg, #70a1ff, #5352ed);
        color: white;
    }
    
    /* Button styling */
    .stButton > button {
        background: var(--background-gradient);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.25);
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div {
        background: var(--background-gradient);
        border-radius: 10px;
    }
    
    /* Chart container */
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    /* Indicator summary */
    .indicator-summary {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e9ecef;
    }
    
    .indicator-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.8rem 0;
        border-bottom: 1px solid #e9ecef;
    }
    
    .indicator-item:last-child {
        border-bottom: none;
    }
    
    .indicator-label {
        font-weight: 600;
        color: var(--dark-color);
    }
    
    .indicator-value {
        font-weight: 700;
        color: var(--primary-color);
    }
    
    /* Alert styling */
    .alert-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .alert-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .alert-info {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    /* Data table styling */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Hide streamlit menu and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--primary-color);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #1565c0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()

if 'alert_system' not in st.session_state:
    st.session_state.alert_system = AlertSystem()

if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False

if 'last_scan_time' not in st.session_state:
    st.session_state.last_scan_time = None

def create_stock_chart(symbol, df):
    """Create comprehensive stock chart with all indicators"""
    if df.empty:
        return None
    
    # Create subplots
    fig = sp.make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.4, 0.2, 0.2, 0.2],
        subplot_titles=(
            f'{symbol.replace(".NS", "")} - Price & Volume',
            'MACD',
            'RSI',
            'MFI'
        )
    )
    
    # Price and Volume
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Price'
        ),
        row=1, col=1
    )
    
    # Volume bars
    colors = ['red' if df['Close'].iloc[i] < df['Open'].iloc[i] else 'green' 
              for i in range(len(df))]
    
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['Volume'],
            name='Volume',
            marker_color=colors,
            opacity=0.7,
            yaxis='y2'
        ),
        row=1, col=1
    )
    
    # MACD
    if 'MACD' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['MACD'],
                name='MACD',
                line=dict(color='blue')
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['MACD_Signal'],
                name='Signal',
                line=dict(color='red')
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['MACD_Histogram'],
                name='Histogram',
                marker_color='gray',
                opacity=0.7
            ),
            row=2, col=1
        )
    
    # RSI
    if 'RSI' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['RSI'],
                name='RSI',
                line=dict(color='purple')
            ),
            row=3, col=1
        )
        
        # RSI levels
        fig.add_hline(y=70, line_dash="dash", line_color="red")
        fig.add_hline(y=30, line_dash="dash", line_color="green")
    
    # MFI
    if 'MFI' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['MFI'],
                name='MFI',
                line=dict(color='orange')
            ),
            row=4, col=1
        )
        
        # MFI levels
        fig.add_hline(y=80, line_dash="dash", line_color="red")
        fig.add_hline(y=20, line_dash="dash", line_color="green")
    
    # Update layout
    fig.update_layout(
        height=800,
        showlegend=True,
        xaxis_rangeslider_visible=False
    )
    
    # Update y-axes
    fig.update_yaxes(title_text="Price (₹)", row=1, col=1)
    fig.update_yaxes(title_text="MACD", row=2, col=1)
    fig.update_yaxes(title_text="RSI", row=3, col=1, range=[0, 100])
    fig.update_yaxes(title_text="MFI", row=4, col=1, range=[0, 100])
    
    return fig

def display_stock_summary(symbol, df):
    """Display stock summary metrics with modern cards"""
    if df.empty:
        return
    
    latest = df.iloc[-1]
    previous = df.iloc[-2] if len(df) > 1 else latest
    
    # Price metrics
    price_change = latest['Close'] - previous['Close']
    price_change_pct = (price_change / previous['Close']) * 100 if previous['Close'] != 0 else 0
    
    # Display metrics with custom cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        delta_class = "positive" if price_change >= 0 else "negative"
        delta_icon = "📈" if price_change >= 0 else "📉"
        st.markdown(f"""
        <div class="metric-card">
            <h3>{symbol.replace('.NS', '')} Price</h3>
            <div class="metric-value">₹{latest['Close']:.2f}</div>
            <div class="metric-delta {delta_class}">
                {delta_icon} {price_change:+.2f} ({price_change_pct:+.2f}%)
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        volume_ratio = latest.get('Volume_Ratio', 1)
        volume_icon = "🔊" if volume_ratio > 1.5 else "🔉"
        st.markdown(f"""
        <div class="metric-card">
            <h3>Volume</h3>
            <div class="metric-value">{format_number(latest['Volume'])}</div>
            <div class="metric-delta">
                {volume_icon} {volume_ratio:.2f}x average
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        rsi_value = latest.get('RSI', 50)
        if rsi_value > 70:
            rsi_status = "Overbought"
            rsi_class = "danger"
            rsi_icon = "⚠️"
        elif rsi_value < 30:
            rsi_status = "Oversold" 
            rsi_class = "success"
            rsi_icon = "✅"
        else:
            rsi_status = "Neutral"
            rsi_class = "info"
            rsi_icon = "ℹ️"
        
        st.markdown(f"""
        <div class="metric-card">
            <h3>RSI</h3>
            <div class="metric-value">{rsi_value:.1f}</div>
            <div class="metric-delta">
                <span class="status-badge {rsi_class}">{rsi_icon} {rsi_status}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        mfi_value = latest.get('MFI', 50)
        if mfi_value > 80:
            mfi_status = "Overbought"
            mfi_class = "danger"
            mfi_icon = "⚠️"
        elif mfi_value < 20:
            mfi_status = "Oversold"
            mfi_class = "success"
            mfi_icon = "✅"
        else:
            mfi_status = "Neutral"
            mfi_class = "info"
            mfi_icon = "ℹ️"
            
        st.markdown(f"""
        <div class="metric-card">
            <h3>MFI</h3>
            <div class="metric-value">{mfi_value:.1f}</div>
            <div class="metric-delta">
                <span class="status-badge {mfi_class}">{mfi_icon} {mfi_status}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def run_signal_scanner():
    """Run signal scanner for all symbols with modern UI"""
    st.markdown("""
    <div class="main-header">
        <h2>📡 Signal Scanner</h2>
        <p>Real-time technical analysis across Nifty 100 stocks</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.spinner("Scanning for signals..."):
        signals_found = []
        
        for symbol in NIFTY_100_SYMBOLS:
            df = load_stock_data(symbol)
            if not df.empty:
                signals = get_latest_signals(symbol, df)
                if signals['signals']:
                    signals_found.append(signals)
        
        st.session_state.last_scan_time = datetime.now()
    
    if signals_found:
        st.markdown(f"""
        <div class="alert-success">
            <strong>Scan Complete!</strong> Found {len(signals_found)} stocks with active signals
        </div>
        """, unsafe_allow_html=True)
        
        # Display signals in a grid
        cols = st.columns(2)
        for i, signal_data in enumerate(signals_found):
            symbol = signal_data['symbol']
            with cols[i % 2]:
                # Determine signal type for styling
                signal_types = [s['type'] for s in signal_data['signals']]
                if any('Bullish' in s or 'Oversold' in s for s in signal_types):
                    card_class = "bullish"
                elif any('Overbought' in s for s in signal_types):
                    card_class = "bearish"
                else:
                    card_class = "neutral"
                
                st.markdown(f"""
                <div class="signal-card {card_class}">
                    <h3>{symbol.replace('.NS', '')}</h3>
                    <p><strong>{len(signal_data['signals'])} Active Signals</strong></p>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander(f"View {symbol.replace('.NS', '')} signals"):
                    for signal in signal_data['signals']:
                        strength_color = "#28a745" if signal['strength'] == 'High' else "#ffc107" if signal['strength'] == 'Medium' else "#6c757d"
                        st.markdown(f"""
                        <div style="padding: 0.5rem; margin: 0.25rem 0; background: #f8f9fa; border-radius: 5px; border-left: 4px solid {strength_color};">
                            <strong>{signal['type']}</strong><br>
                            {signal['message']}<br>
                            <small style="color: {strength_color};">Strength: {signal['strength']}</small>
                        </div>
                        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="alert-info">
            <strong>Scan Complete!</strong> No signals detected in current market conditions
        </div>
        """, unsafe_allow_html=True)

# Main Application
def main():
    # Modern header
    st.markdown("""
    <div class="main-header">
        <h1>📈 Nifty 100 Stock Analysis Dashboard</h1>
        <p>Advanced technical analysis for Nifty 100 stocks with automated alerts</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar with modern styling
    st.sidebar.markdown("""
    <div class="sidebar-section">
        <h2 style="margin-top: 0;">⚡ Dashboard Controls</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Data management section
    st.sidebar.markdown("""
    <div class="sidebar-section">
        <h3>📊 Data Management</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("📥 Download All Data", help="Download latest data for all Nifty 100 stocks"):
        with st.spinner("Downloading data for all Nifty 100 stocks..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            result = st.session_state.data_manager.download_batch_data(
                NIFTY_100_SYMBOLS, 
                progress_bar, 
                status_text
            )
            
            if result['successful'] > 0:
                st.markdown(f"""
                <div class="alert-success">
                    <strong>Success!</strong> Downloaded {result['successful']}/{result['total']} stocks successfully
                </div>
                """, unsafe_allow_html=True)
            
            if result['failed']:
                st.markdown(f"""
                <div class="alert-warning">
                    <strong>Partial Success:</strong> Failed to download: {', '.join(result['failed'][:5])}
                    {f"... and {len(result['failed'])-5} more" if len(result['failed']) > 5 else ""}
                </div>
                """, unsafe_allow_html=True)
    
    # Stock selection
    st.sidebar.markdown("""
    <div class="sidebar-section">
        <h3>🎯 Stock Analysis</h3>
    </div>
    """, unsafe_allow_html=True)
    
    selected_stock = st.sidebar.selectbox(
        "Select a stock to analyze:",
        NIFTY_100_SYMBOLS,
        format_func=lambda x: x.replace('.NS', ''),
        help="Choose from Nifty 100 stocks for detailed analysis"
    )
    
    # Analysis options with modern styling
    st.sidebar.markdown("**Display Options:**")
    show_chart = st.sidebar.checkbox("📊 Technical Chart", value=True)
    show_summary = st.sidebar.checkbox("📋 Summary Cards", value=True)
    
    # Alert system
    st.sidebar.markdown("""
    <div class="sidebar-section">
        <h3>🔔 Alert System</h3>
    </div>
    """, unsafe_allow_html=True)
    
    email_configured = validate_email_config()
    
    if email_configured:
        st.sidebar.markdown("""
        <div style="background: #d4edda; padding: 0.75rem; border-radius: 6px; border: 1px solid #c3e6cb; color: #155724; margin-bottom: 1rem;">
            <strong>✅ Email Configured</strong><br>
            <small>Ready to send alerts</small>
        </div>
        """, unsafe_allow_html=True)
        
        if st.sidebar.button("🔔 Send Test Alert", help="Test your email configuration"):
            if st.session_state.alert_system.send_email_alert(
                "Test Alert", 
                "This is a test alert from your Nifty 100 Dashboard"
            ):
                st.sidebar.markdown("""
                <div style="background: #d4edda; padding: 0.5rem; border-radius: 4px; color: #155724;">
                    Test alert sent successfully!
                </div>
                """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown("""
        <div style="background: #fff3cd; padding: 0.75rem; border-radius: 6px; border: 1px solid #ffeaa7; color: #856404; margin-bottom: 1rem;">
            <strong>⚠️ Email Not Configured</strong><br>
            <small>Set EMAIL_USER, EMAIL_PASSWORD, and EMAIL_RECIPIENTS environment variables</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Scanner section
    st.sidebar.markdown("""
    <div class="sidebar-section">
        <h3>📡 Signal Scanner</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("🔍 Run Signal Scan", help="Scan all Nifty 100 stocks for trading signals"):
        run_signal_scanner()
    
    if st.session_state.last_scan_time:
        st.sidebar.markdown(f"""
        <div style="background: #f8f9fa; padding: 0.5rem; border-radius: 4px; border-left: 3px solid #007bff; margin: 0.5rem 0;">
            <small><strong>Last scan:</strong> {st.session_state.last_scan_time.strftime('%H:%M:%S')}</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Auto-refresh with modern toggle
    st.sidebar.markdown("**Settings:**")
    auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (60s)", value=st.session_state.auto_refresh)
    st.session_state.auto_refresh = auto_refresh
    
    # Main content area
    if selected_stock:
        # Load stock data
        df = st.session_state.data_manager.get_stock_data(selected_stock)
        
        if df.empty:
            st.warning(f"No data available for {selected_stock}")
            st.info("Click 'Download All Data' to fetch historical data")
        else:
            # Display summary
            if show_summary:
                display_stock_summary(selected_stock, df)
                st.markdown("---")
            
            # Display chart
            if show_chart:
                st.markdown(f"""
                <div class="chart-container">
                    <h2>📊 Technical Analysis - {selected_stock.replace('.NS', '')}</h2>
                </div>
                """, unsafe_allow_html=True)
                
                chart = create_stock_chart(selected_stock, df)
                if chart:
                    # Update chart theme for modern look
                    chart.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(family="Arial, sans-serif", size=12),
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    st.plotly_chart(chart, use_container_width=True)
                
                # Display indicator summary with modern cards
                indicators = get_indicator_summary(df)
                if indicators:
                    st.markdown("""
                    <h2 style="margin-top: 2rem;">🎯 Technical Indicators Summary</h2>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # MACD Card
                        macd_data = indicators.get('MACD', {})
                        st.markdown(f"""
                        <div class="indicator-summary">
                            <h3>📈 MACD</h3>
                            <div class="indicator-item">
                                <span class="indicator-label">MACD Line:</span>
                                <span class="indicator-value">{macd_data.get('value', 0):.4f}</span>
                            </div>
                            <div class="indicator-item">
                                <span class="indicator-label">Signal Line:</span>
                                <span class="indicator-value">{macd_data.get('signal', 0):.4f}</span>
                            </div>
                            <div class="indicator-item">
                                <span class="indicator-label">Histogram:</span>
                                <span class="indicator-value">{macd_data.get('histogram', 0):.4f}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Volume Card
                        volume_data = indicators.get('Volume', {})
                        st.markdown(f"""
                        <div class="indicator-summary">
                            <h3>📊 Volume Analysis</h3>
                            <div class="indicator-item">
                                <span class="indicator-label">Current Volume:</span>
                                <span class="indicator-value">{format_number(volume_data.get('current', 0))}</span>
                            </div>
                            <div class="indicator-item">
                                <span class="indicator-label">Volume Ratio:</span>
                                <span class="indicator-value">{volume_data.get('ratio', 1):.2f}x</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        # RSI Card
                        rsi_data = indicators.get('RSI', {})
                        rsi_value = rsi_data.get('value', 50)
                        rsi_condition = ""
                        if rsi_data.get('oversold'):
                            rsi_condition = '<span class="status-badge success">🔻 Oversold</span>'
                        elif rsi_data.get('overbought'):
                            rsi_condition = '<span class="status-badge danger">🔺 Overbought</span>'
                        else:
                            rsi_condition = '<span class="status-badge info">➡️ Neutral</span>'
                        
                        st.markdown(f"""
                        <div class="indicator-summary">
                            <h3>⚡ RSI</h3>
                            <div class="indicator-item">
                                <span class="indicator-label">RSI Value:</span>
                                <span class="indicator-value">{rsi_value:.2f}</span>
                            </div>
                            <div class="indicator-item">
                                <span class="indicator-label">Condition:</span>
                                <span>{rsi_condition}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # MFI Card
                        mfi_data = indicators.get('MFI', {})
                        mfi_value = mfi_data.get('value', 50)
                        mfi_condition = ""
                        if mfi_data.get('oversold'):
                            mfi_condition = '<span class="status-badge success">🔻 Oversold</span>'
                        elif mfi_data.get('overbought'):
                            mfi_condition = '<span class="status-badge danger">🔺 Overbought</span>'
                        else:
                            mfi_condition = '<span class="status-badge info">➡️ Neutral</span>'
                        
                        st.markdown(f"""
                        <div class="indicator-summary">
                            <h3>💰 MFI</h3>
                            <div class="indicator-item">
                                <span class="indicator-label">MFI Value:</span>
                                <span class="indicator-value">{mfi_value:.2f}</span>
                            </div>
                            <div class="indicator-item">
                                <span class="indicator-label">Condition:</span>
                                <span>{mfi_condition}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
    
    # Data status with modern styling
    st.sidebar.markdown("""
    <div class="sidebar-section">
        <h3>📊 Data Status</h3>
    </div>
    """, unsafe_allow_html=True)
    
    status = get_stock_status_summary(NIFTY_100_SYMBOLS)
    
    # Create status indicators
    total_stocks = len(NIFTY_100_SYMBOLS)
    loaded_pct = (status['loaded'] / total_stocks * 100) if total_stocks > 0 else 0
    
    st.sidebar.markdown(f"""
    <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span>✅ Loaded:</span>
            <strong style="color: #28a745;">{status['loaded']}</strong>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span>❌ Missing:</span>
            <strong style="color: #dc3545;">{status['missing']}</strong>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span>⚠️ Errors:</span>
            <strong style="color: #ffc107;">{status['error']}</strong>
        </div>
        <div style="background: #e9ecef; border-radius: 10px; height: 8px; margin-top: 0.75rem;">
            <div style="background: linear-gradient(90deg, #28a745, #20c997); height: 100%; border-radius: 10px; width: {loaded_pct}%;"></div>
        </div>
        <small style="color: #6c757d;">Data Coverage: {loaded_pct:.1f}%</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Auto-refresh logic
    if st.session_state.auto_refresh:
        time.sleep(REFRESH_INTERVAL)
        st.rerun()

if __name__ == "__main__":
    main()

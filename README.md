# SmartScan - NSE Market Analysis Tool 📈

A comprehensive technical analysis tool for scanning and evaluating Nifty 50 stocks using advanced indicators and automated reporting.

## Features 🚀

- **Data Collection**: 
  - Automated fetching of Nifty 50 stock data
  - Local SQLite database storage for historical data
  - Configurable time periods (daily, weekly, monthly)
  - Real-time data updates via yfinance API

- **Technical Analysis**: 
  - **Core Indicators**:
    - RSI (Relative Strength Index)
    - MACD (Moving Average Convergence Divergence)
    - Simple Moving Averages (20 and 50-day)
    - Volume Analysis with trend detection
  
  - **Signal Generation**:
    - Multi-factor scoring system
    - Trend strength analysis
    - Volume confirmation
    - Price momentum evaluation

  - **Technical Charts**:
    - Candlestick patterns
    - Volume subplot
    - RSI indicator panel
    - MACD histogram and signal lines
    - Moving averages overlay

- **Signal Strength Calculation**:
  - **Scoring Components**:
    - Price trend relative to moving averages
    - RSI momentum and zones
    - MACD crossovers and histogram
    - Volume trend confirmation
    - Recent price action

  - **Signal Categories**:
    - Strong Buy (Strength > 3.0)
    - Buy (Strength 1.0 to 3.0)
    - Neutral (Strength -1.0 to 1.0)
    - Sell (Strength -3.0 to -1.0)
    - Strong Sell (Strength < -3.0)

- **Automated Reporting**: 
  - Comprehensive markdown reports
  - Technical analysis charts
  - Signal strength metrics
  - Volume profile analysis
  - Key support/resistance levels

- **Interactive HTML Dashboard**: 
  - **Real-time Visualization**:
    - Responsive web interface
    - Dark/light theme support
    - Mobile-friendly design
  
  - **Market Overview**:
    - Nifty 50 Index analysis
    - Interactive technical charts
    - Market sentiment indicators
    - Signal distribution metrics

  - **Stock Analysis Cards**:
    - Detailed technical metrics
    - Signal strength indicators
    - Price and volume data
    - Expandable charts
    - Quick filtering and search

  - **Features**:
    - Dynamic stock filtering
    - Signal-based sorting
    - Real-time search
    - Chart modal view
    - Responsive grid layout

## Dashboard Access 🌐

The interactive technical analysis dashboard is available at: [SmartScan Dashboard](https://finstraddle.github.io/smartscan/)

Features:
- View Nifty 50 Index overview and market sentiment
- Filter stocks by signal strength (Buy/Sell)
- Search for specific stocks
- Sort by various technical indicators
- Toggle between dark/light themes
- View detailed technical charts

## Installation 🔧

1. Clone the repository:
```bash
git clone https://github.com/finstraddle/smartscan.git
cd smartscan
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage 💻

### Command Line Interface

```bash
python -m src.cli.command_line [options]
```

### Command Line Options:

- **Data Collection Options**:
  - `--period`: Data fetch period (default: 3mo)
    - Valid values: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max
  - `--interval`: Data interval (default: 1d)
    - Valid values: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo

- **Analysis Options**:
  - `--min-strength`: Minimum signal strength to display (default: 1.0)
  - `--save-report`: Generate and save analysis report
  - `--chart`: Generate technical analysis charts
  - `--db-update`: Force update of local database

- **Output Options**:
  - `--output-dir`: Custom output directory for reports
  - `--format`: Report format (md/html, default: md)

### Examples:

1. Basic scan with default settings:
```bash
python -m src.cli.command_line --save-report
```

2. Detailed analysis with charts:
```bash
python -m src.cli.command_line --period 6mo --min-strength 1.5 --save-report --chart
```

3. Intraday analysis:
```bash
python -m src.cli.command_line --period 5d --interval 15m --save-report
```

## Technical Analysis Methodology 📊

### Signal Strength Calculation

The signal strength is calculated using a weighted combination of factors:

1. **Trend Analysis (40%)**:
   - Price position relative to SMAs
   - Moving average crossovers
   - Recent price momentum

2. **Momentum Indicators (30%)**:
   - RSI zones and crossovers
   - MACD signal line crossovers
   - MACD histogram momentum

3. **Volume Analysis (30%)**:
   - Volume trend
   - Price-volume relationship
   - Volume ratio vs average

### Scoring System

- Each component contributes to the final signal strength (-4.0 to +4.0)
- Positive scores indicate bullish signals
- Negative scores indicate bearish signals
- Magnitude indicates signal strength
- Volume acts as a confirmation/adjustment factor

## Version History 📝

### v1.1 (Latest)
- Added Nifty 50 Index (^NSEI) analysis
- Extended data collection period to 1 year (from 3 months)
- Enhanced report generation with index overview section
- Improved signal strength calculations
- Added dedicated charts for index analysis

### v1.0
- Initial release with core functionality
- Basic technical analysis for Nifty 50 stocks
- Automated report generation
- Technical charts and indicators

## Project Structure 📁

```
smartscan/
├── src/
│   ├── analysis/          # Technical analysis modules
│   ├── data_collection/   # Data fetching and storage
│   ├── visualization/     # Chart generation
│   ├── output/           # Report generation
│   └── cli/             # Command line interface
├── drafts/              # Generated reports
├── data/               # SQLite database
└── requirements.txt
```

## Requirements 📋

- Python 3.12+
- pandas
- numpy
- yfinance
- ta (Technical Analysis library)
- mplfinance
- matplotlib
- sqlite3

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

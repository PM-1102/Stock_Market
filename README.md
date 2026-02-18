# SENSEX Futures VWAP Monitoring System

Real-time monitoring system for SENSEX Futures with tick-level VWAP calculation and PCR-based signal generation.

## Overview

This system connects to Dhan's WebSocket API to receive live market data for SENSEX Futures, calculates Volume-Weighted Average Price (VWAP) at the tick level, and generates trading signals based on Put-Call Ratio (PCR) when price touches VWAP.

### Key Features

- **Real-time Data**: Live tick-by-tick data via Dhan WebSocket API
- **Tick-Level VWAP**: Mathematically accurate VWAP calculation updated on every trade
- **Session-Anchored**: VWAP automatically resets at market open (9:15 AM IST)
- **5-Minute Candles**: Automatic OHLCV candle construction from tick data
- **PCR Calculation**: Automatic Put-Call Ratio calculation when price touches VWAP
- **Signal Generation**: Buy/Sell signals based on PCR values (monitoring only, no orders placed)
- **Ping/Pong Management**: Automatic connection keep-alive to prevent timeouts

## Requirements

### Python Version
- Python 3.7 or higher

### Dependencies
```bash
pip install websocket-client requests
```

### Dhan Account Requirements
- Active Dhan trading account
- DhanHQ API credentials (Access Token & Client ID)
- DhanHQ Data APIs subscription (₹499/month) for WebSocket access

## Installation

### 1. Clone or Download Files

Ensure you have all 5 core files:
- `main.py` - Main WebSocket handler
- `vwap_engine.py` - VWAP calculation engine
- `candle_builder.py` - 5-minute candle builder
- `dhan_client.py` - Dhan API client
- `config.py` - Configuration file

### 2. Install Dependencies

```bash
pip install websocket-client requests
```

### 3. Configure Credentials

Edit `config.py` and add your Dhan API credentials:

```python
ACCESS_TOKEN = "your_dhan_access_token_here"
CLIENT_ID = "your_dhan_client_id_here"
```

**Getting Your Credentials:**
1. Log in to Dhan: https://web.dhan.co/
2. Navigate to: Settings → API → Generate Token
3. Copy the Access Token (valid for 24 hours)
4. Copy your Client ID from account settings

## Usage

### Running the System

```bash
python main.py
```

### Initial Configuration

On startup, you'll be prompted to configure:

```
Choose Entry Timing:
1 - Candle Close
2 - Last N seconds before close
Enter choice (1 or 2): 1

Enter SL %: 2
Enter TP %: 4
```

**Parameters:**
- **Entry Timing**: When to consider entry signals (candle close or N seconds before)
- **SL %**: Stop Loss percentage (for future reference, not executed)
- **TP %**: Take Profit percentage (for future reference, not executed)

### Sample Output

```
============================================================
SENSEX FUTURES VWAP MONITORING SYSTEM
============================================================

WebSocket Connected

[10:15:03] LTP: 83586.90 | Vol:    40 | VWAP: 83593.45
[10:15:04] LTP: 83590.00 | Vol:    15 | VWAP: 83592.18
[10:15:05] LTP: 83588.50 | Vol:    62 | VWAP: 83591.95

==================== CANDLE CLOSED ====================

VWAP TOUCH DETECTED!
   Current Price: 83586.90
   VWAP: 83593.63

Fetching Option Chain...
Using nearest expiry: 2026-02-26
Retrieved option chain with 45 strikes

PCR Calculation:
   Total Put OI: 12,345,678
   Total Call OI: 10,987,654
   PCR: 1.1236

Trade Signal Generated: BUY CALL (PCR: 1.1236)
```

## System Architecture

### Data Flow

```
Dhan WebSocket API
        ↓
    Tick Data (LTP, Volume, Timestamp)
        ↓
    ├─→ VWAP Engine (tick-level calculation)
    ├─→ Candle Builder (5-min OHLCV aggregation)
    └─→ VWAP Touch Detection
            ↓
        Option Chain API (fetch PCR data)
            ↓
        Signal Generation (BUY CALL / BUY PUT)
```

### File Structure

```
project/
│
├── main.py              # WebSocket handler & main logic
├── vwap_engine.py       # VWAP calculation engine
├── candle_builder.py    # Candle aggregation
├── dhan_client.py       # Dhan API client
├── config.py            # API credentials
└── README.md            # This file
```

## Key Components

### 1. VWAP Engine (`vwap_engine.py`)

Calculates session-anchored VWAP using the formula:

```
VWAP = Σ(Price × Volume) / Σ(Volume)
```

**Features:**
- Updates on every tick (not candle)
- Automatically resets at 9:15 AM IST daily
- Uses cumulative sum for mathematical accuracy

### 2. Candle Builder (`candle_builder.py`)

Constructs 5-minute OHLCV candles from tick data.

**Intervals:** 
- 9:15-9:20, 9:20-9:25, 9:25-9:30, etc.

### 3. Dhan Client (`dhan_client.py`)

Handles communication with Dhan's REST API for:
- Fetching available expiry dates
- Retrieving option chain data
- Automatic rate limiting (3-second intervals)

### 4. Main Controller (`main.py`)

Orchestrates all components:
- WebSocket connection management
- Tick data processing
- VWAP touch detection
- PCR-based signal generation
- Threading for non-blocking API calls

## Configuration

### Security ID

Currently monitoring SENSEX Futures February 2026:
```python
SECURITY_ID = "1165486"  # BSE SENSEX FEB 2026 FUT
```

**To change instrument:**
1. Download Dhan scrip master CSV
2. Find the Security ID for your desired instrument
3. Update `SECURITY_ID` in `main.py`

### VWAP Touch Threshold

Default: 10 points

```python
vwap_touch_threshold = 10  # Trigger when price within 10 points of VWAP
```

Adjust in `main.py` based on volatility and your strategy.

### Session Timing

Default: 9:15 AM - 3:30 PM IST

```python
vwap_engine = SessionVWAP(session_start_hour=9, session_start_minute=15)
```

## Trading Logic

### VWAP Touch Detection

When `|Current Price - VWAP| ≤ threshold`:
1. System detects VWAP touch
2. Fetches option chain data
3. Calculates PCR

### PCR-Based Signals

```
PCR > 1.0  →  More Put OI  →  Bearish Sentiment  →  BUY CALL
PCR < 1.0  →  More Call OI →  Bullish Sentiment →  BUY PUT
```

**Note:** This is monitoring only. No orders are placed automatically.

## Troubleshooting

### WebSocket Connection Issues

**Error:** "Connection to remote host was lost"

**Causes:**
1. Access Token expired (24-hour validity)
2. No DhanHQ Data API subscription
3. Invalid Client ID
4. Network/firewall blocking WebSocket

**Solutions:**
1. Regenerate Access Token from Dhan
2. Verify Data API subscription is active
3. Check credentials in `config.py`
4. Test connection from different network

### Volume Shows Zero

**Cause:** Most Quote updates contain price changes without new trades.

**Expected:** System only processes ticks with `volume_delta > 0`, skipping redundant updates.

### Session Reset at Wrong Time

**Expected:** VWAP resets only once on first connection, then daily at 9:15 AM.

**If resetting mid-session:** Check system time and timezone settings.

### PCR Calculation Fails

**Causes:**
1. Option chain API rate limit (3 seconds)
2. Invalid expiry date
3. Network timeout

**Solutions:**
1. Wait for rate limit period
2. Verify expiry date format (YYYY-MM-DD)
3. Increase timeout in `dhan_client.py`

## Important Notes

### Token Validity

- Dhan Access Tokens expire after 24 hours
- Regenerate daily or before market open
- System will fail to connect with expired token

### Market Hours

- BSE F&O: 9:15 AM - 3:30 PM IST
- System only works during market hours
- WebSocket will disconnect after market close

### Data API Subscription

Required for WebSocket access. Without it:
- REST APIs work (option chain, etc.)
- WebSocket connections fail immediately

### Volume Accuracy

Using `last_qty` as fallback when `total_volume` delta is zero. This is accurate for individual trades but may not capture exact tick-by-tick volume distribution in high-frequency scenarios.

### No Order Execution

This is a **monitoring and analysis tool only**. It does not:
- Place orders automatically
- Execute trades
- Manage positions
- Handle risk management

Use signals as informational only. Manual trading decisions required.

## Advanced Configuration

### Custom Instruments

To monitor NIFTY instead of SENSEX:

```python
# In main.py
SECURITY_ID = "26000"  # NIFTY Futures

# In dhan_client.py (for option chain)
underlying_scrip = 13  # NIFTY Index
```

### Multiple Instruments

Currently supports single instrument. For multiple:
1. Subscribe to multiple instruments in `on_open()`
2. Maintain separate `vwap_engine` instances
3. Use instrument ID to route data

### Historical Backtesting

To backtest on historical data:
1. Use Dhan Historical API to fetch tick/candle data
2. Feed to `vwap_engine` and `candle_builder`
3. Simulate VWAP touch and PCR calculations
4. Analyze signal performance

## Performance Optimization

### Tick Processing

System skips ticks with zero volume to reduce:
- CPU usage
- Log spam
- Processing lag

### Threaded API Calls

Option chain fetching runs in background thread to prevent:
- WebSocket ping/pong timeout
- Data processing delays
- Connection drops

### Ping/Pong Keep-Alive

```python
ws.run_forever(ping_interval=20, ping_timeout=10)
```

Maintains connection during low-activity periods.

## License

This project is for educational and personal use only. 

**Disclaimer:** 
- Not financial advice
- Use at your own risk
- Past performance does not guarantee future results
- Always verify signals before trading
- Ensure proper risk management

## Support

For issues or questions:
1. Check Dhan API documentation: https://dhanhq.co/docs/v2/
2. Verify credentials and subscription status
3. Review console output for error messages
4. Test individual components separately

## Changelog

### Version 1.0 (Current)
- Initial release
- Tick-level VWAP calculation
- Session-anchored reset
- 5-minute candle building
- PCR-based signal generation
- WebSocket ping/pong management
- Threaded API calls for performance

---

**Created:** February 2026  
**Market:** BSE F&O (SENSEX Futures)  
**Trading Hours:** 9:15 AM - 3:30 PM IST  
**Mode:** Monitoring Only (No Automated Trading)

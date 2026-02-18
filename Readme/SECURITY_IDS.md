# 📋 SECURITY ID REFERENCE

## Important: Correct Security IDs for Your Code

Based on your original dhan_client.py, you're using:
- **SENSEX Security ID: 51**
- **Segment: IDX_I** (Index)

---

## Common Security IDs

### For Futures Trading:
| Instrument | Security ID | Segment | Notes |
|-----------|-------------|---------|-------|
| SENSEX Futures | Check Dhan instruments file | BSE_FNO | Changes monthly |
| NIFTY Futures | Check Dhan instruments file | NSE_FNO | Changes monthly |

### For Options (Your Use Case):
| Underlying Index | Security ID | Segment | Used For |
|-----------------|-------------|---------|----------|
| SENSEX | **51** | IDX_I | Option Chain |
| NIFTY | **13** | IDX_I | Option Chain |
| BANKNIFTY | **25** | IDX_I | Option Chain |
| FINNIFTY | **27** | IDX_I | Option Chain |

---

## Your Current Configuration

In your code, you're monitoring:
- **WebSocket:** SENSEX Futures (BSE_FNO, SecurityId: "1165486")
- **Option Chain:** SENSEX Index (Security ID: 51)

This is **CORRECT** ✅

The futures contract ID (1165486) is for live price monitoring.
The index ID (51) is for fetching option chain data.

---

## How to Find Security IDs

### Method 1: Dhan Instruments File
Download from: https://dhanhq.co/docs/v2/instruments/

### Method 2: API Explorer
Use Dhan's API documentation to search for instruments.

### Method 3: Your Broker Platform
Security IDs are often shown in the trading terminal.

---

## Important Notes

1. **Futures Security IDs change monthly** (as contracts expire)
2. **Option Chain uses underlying index ID** (stays constant)
3. **Your code correctly uses both:**
   - Futures ID for price monitoring (1165486)
   - Index ID for option chain (51)

---

## If You Want to Switch to NIFTY

Change in `main.py`:
```python
# For WebSocket (futures monitoring)
"SecurityId": "NIFTY_CURRENT_MONTH_FUTURES_ID"  # Check instruments file

# For option chain (in check_vwap_touch function)
option_chain = client.fetch_option_chain(
    underlying_scrip=13,  # NIFTY
    underlying_seg="IDX_I"
)
```

---

**Your current setup is correct for SENSEX monitoring! ✅**

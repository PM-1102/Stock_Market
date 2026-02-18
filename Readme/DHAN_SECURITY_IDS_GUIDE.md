# 🔍 DHAN SECURITY IDS - COMPLETE GUIDE FOR SENSEX

## Overview

Dhan uses **different Security IDs** for different purposes:
1. **Index Security ID** → For Option Chain API (stays constant)
2. **Futures Security ID** → For live price data via WebSocket (changes monthly)

---

## Quick Reference

### Based on Your Original Code:

| Purpose | Security ID | Segment | Usage |
|---------|-------------|---------|-------|
| **Option Chain** | **51** | IDX_I | `fetch_option_chain(underlying_scrip=51)` |
| **WebSocket (Futures)** | **1165486** | BSE_FNO | `"SecurityId": "1165486"` |

### Verification Status:
- ✅ **Security ID 51 (SENSEX Index)** - Used correctly in your dhan_client.py
- ⚠️ **Security ID 1165486 (SENSEX Futures)** - Need to verify if current month

---

## How to Find Correct Security IDs

### Method 1: Run the Analyzer Script (Recommended)

I've created `find_sensex_ids.py` which will:
1. Download the latest Dhan scrip master CSV
2. Filter for SENSEX instruments
3. Show you the correct Security IDs for current month

**To run:**
```bash
pip install pandas requests
python find_sensex_ids.py
```

### Method 2: Manual Download

1. Download CSV from:
   ```
   https://images.dhan.co/api-data/api-scrip-master-detailed.csv
   ```

2. Open in Excel/Google Sheets

3. Filter for SENSEX:
   - **For Option Chain:** Look for SENSEX in IDX_I segment (no expiry)
   - **For Futures:** Look for SENSEX in BSE_FNO segment (check expiry date)

### Method 3: Use Dhan API

```python
from dhanhq import dhanhq

dhan = dhanhq("client_id", "access_token")

# Fetch instrument list for BSE F&O
instruments = dhan.fetch_security_list("BSE_FNO")

# Filter for SENSEX futures
sensex_futures = [
    inst for inst in instruments 
    if 'SENSEX' in inst['tradingsymbol'] 
    and inst['instrument_type'] == 'FUTIDX'
]
```

---

## Understanding Dhan Security IDs

### 1. Index Security IDs (For Option Chain)

**SENSEX Index:**
- Security ID: **51**
- Segment: **IDX_I** (Index)
- Usage: Option Chain API
- **Does NOT change** monthly

**In your code:**
```python
# dhan_client.py
payload = {
    "UnderlyingScrip": 51,        # SENSEX Index
    "UnderlyingSeg": "IDX_I",     # Index segment
    "Expiry": "2026-02-19"        # Option expiry (auto-selected)
}
```

### 2. Futures Security IDs (For Live Data)

**SENSEX Futures:**
- Security ID: Changes every month (e.g., **1165486** for one month)
- Segment: **BSE_FNO** (BSE Futures & Options)
- Usage: WebSocket live market feed
- **Changes monthly** when contract expires

**In your code:**
```python
# main.py
payload = {
    "RequestCode": 17,
    "InstrumentList": [{
        "ExchangeSegment": "BSE_FNO",
        "SecurityId": "1165486"     # SENSEX Futures (current month)
    }]
}
```

---

## Common Confusion: Why Two Different IDs?

### Scenario: SENSEX Monitoring

**For Option Chain (PCR Calculation):**
- You need the **INDEX** security ID (51)
- This represents the SENSEX index itself
- Used to fetch all CALL and PUT options

**For Live Price Data:**
- You need the **FUTURES** security ID (1165486)
- This represents the current month futures contract
- Used to get real-time price ticks

**Both are needed for your project!**

---

## How Futures Security IDs Work

SENSEX Futures contracts:
- **Expire monthly** (last Thursday of each month)
- **New contract** for each month with different Security ID
- **Current month** = "Near month" contract (most liquid)

### Example Timeline:

| Month | Expiry Date | Security ID | Status |
|-------|-------------|-------------|--------|
| Jan 2026 | 30-Jan-2026 | 1165401 | Expired |
| **Feb 2026** | **27-Feb-2026** | **1165486** | **Current** ⭐ |
| Mar 2026 | 27-Mar-2026 | 1165532 | Next month |

⚠️ **When Feb contract expires on 27-Feb-2026:**
- Security ID 1165486 becomes inactive
- Need to update code to March contract ID (1165532)

---

## Updating Your Code Monthly

### Option 1: Manual Update (Simple)

Before the last Thursday of each month:
1. Run `find_sensex_ids.py`
2. Get new Security ID
3. Update in `main.py`:
   ```python
   "SecurityId": "NEW_SECURITY_ID_HERE"
   ```

### Option 2: Automatic Selection (Advanced)

Modify main.py to fetch current month contract:
```python
# At startup, fetch and select current month futures
def get_current_sensex_futures_id():
    """Get current month SENSEX futures Security ID"""
    # Download scrip master
    # Filter for SENSEX BSE_FNO
    # Sort by expiry date
    # Return first (nearest expiry)
    pass

# Then use in WebSocket subscription
current_future_id = get_current_sensex_futures_id()
```

---

## Verification Checklist

Before running your system:

- [ ] **Option Chain ID verified:** Should be 51 for SENSEX ✅
- [ ] **Futures ID verified:** Check if 1165486 is current month
- [ ] **Expiry date checked:** Is it before 27-Feb-2026?
- [ ] **Scrip master downloaded:** Latest version analyzed
- [ ] **WebSocket connects:** Test during market hours

---

## Common Issues & Solutions

### Issue 1: "Invalid Security ID" on WebSocket
**Cause:** Futures contract expired, Security ID no longer valid  
**Solution:** Update to current month Security ID using analyzer script

### Issue 2: "No data received" on WebSocket
**Cause:** Wrong segment or expired contract  
**Solution:** Verify Security ID is for BSE_FNO segment and current month

### Issue 3: Option Chain returns empty
**Cause:** Wrong underlying scrip ID  
**Solution:** Use 51 for SENSEX Index (not futures ID)

### Issue 4: PCR calculation wrong
**Cause:** Using futures ID instead of index ID  
**Solution:** Option Chain needs index ID (51), not futures ID

---

## Quick Test: Verify Your Security IDs

Run this test during market hours:

```python
# test_security_ids.py
import websocket
import json
from config import ACCESS_TOKEN, CLIENT_ID

# Test WebSocket with your Futures ID
url = f"wss://api-feed.dhan.co?version=2&token={ACCESS_TOKEN}&clientId={CLIENT_ID}&authType=2"

def on_open(ws):
    payload = {
        "RequestCode": 17,
        "InstrumentCount": 1,
        "InstrumentList": [{
            "ExchangeSegment": "BSE_FNO",
            "SecurityId": "1165486"  # Your current ID
        }]
    }
    ws.send(json.dumps(payload))
    print("✅ Subscription sent")

def on_message(ws, message):
    if isinstance(message, bytes):
        print("✅ Receiving data - Security ID is VALID!")
        ws.close()
    else:
        print(f"Response: {message}")

def on_error(ws, error):
    print(f"❌ Error: {error}")
    print("⚠️  Security ID might be invalid or expired")

ws = websocket.WebSocketApp(url, on_open=on_open, on_message=on_message, on_error=on_error)
ws.run_forever()
```

If you get data → Security ID is correct ✅  
If you get error → Run `find_sensex_ids.py` to get current ID

---

## Summary: Your Current Configuration

**Based on your original code:**

```python
# For Option Chain (PCR calculation)
underlying_scrip = 51              # ✅ CORRECT (SENSEX Index)
underlying_seg = "IDX_I"           # ✅ CORRECT

# For WebSocket (Live price)
security_id = "1165486"            # ⚠️ VERIFY if current month
exchange_segment = "BSE_FNO"       # ✅ CORRECT
```

**Action Required:**
1. ✅ Option Chain ID (51) is correct - no change needed
2. ⚠️ Run `find_sensex_ids.py` to verify Futures ID (1165486) is current month

---

## Files Provided

1. **find_sensex_ids.py** - Run this to get correct Security IDs
2. **This guide** - Reference for understanding Security IDs
3. **test_security_ids.py** - Quick verification test

---

**Run the analyzer script now to verify your Security IDs!**

```bash
python find_sensex_ids.py
```

This will download the latest scrip master and show you:
- Current SENSEX Futures Security ID (for WebSocket)
- SENSEX Index Security ID (for Option Chain)
- Whether your current IDs are correct or need updating

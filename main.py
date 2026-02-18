import websocket
import json
import struct
import time
import threading # Required to fix the ping/pong timeout
from datetime import datetime
from config import ACCESS_TOKEN, CLIENT_ID
from candle_builder import CandleBuilder
from vwap_engine import SessionVWAP
from dhan_client import DhanClient

# --- CONFIGURATION ---
print("Choose Entry Timing:")
print("1 - Candle Close")
print("2 - Last N seconds before close")

entry_choice = input("Enter choice (1 or 2): ").strip()

entry_seconds = 0
if entry_choice == "2":
    entry_seconds = int(input("Enter seconds before close: ").strip())

sl_percent = float(input("Enter SL %: ").strip())
tp_percent = float(input("Enter TP %: ").strip())

print("\nConfiguration Locked.")
print("========================================\n")

# --- INITIALIZATION ---
candle_builder = CandleBuilder()
vwap_engine = SessionVWAP(session_start_hour=9, session_start_minute=15)
client = DhanClient()

trade_triggered = False
vwap_touch_threshold = 10
url = f"wss://api-feed.dhan.co?version=2&token={ACCESS_TOKEN}&clientId={CLIENT_ID}&authType=2"
SECURITY_ID = "1165486"

def calculate_pcr(option_chain_response):
    data_block = option_chain_response.get("data", {})
    oc_data = data_block.get("oc", {})
    total_put_oi = 0
    total_call_oi = 0
    for strike, values in oc_data.items():
        total_call_oi += values.get("ce", {}).get("oi", 0)
        total_put_oi += values.get("pe", {}).get("oi", 0)

    if total_call_oi == 0: return 0
    pcr = total_put_oi / total_call_oi
    print(f"\nPCR Calculation:\n   Total Put OI: {total_put_oi:,}\n   Total Call OI: {total_call_oi:,}\n   PCR: {pcr:.4f}")
    return pcr

def background_signal_check(ltp, vwap):
    """Handles the heavy API call in a separate thread to prevent WebSocket timeout."""
    global trade_triggered
    print(f"\nVWAP TOUCH DETECTED!\n   Current Price: {ltp:.2f}\n   VWAP: {vwap:.2f}")
    try:
        print("\nFetching Option Chain...")
        option_chain = client.fetch_option_chain(underlying_scrip=51, underlying_seg="IDX_I")
        if option_chain:
            pcr = calculate_pcr(option_chain)
            signal = "BUY CALL" if pcr > 1.0 else "BUY PUT"
            print(f"\nTrade Signal Generated: {signal} (PCR: {pcr:.4f})")
        else:
            print("Failed to fetch option chain")
            trade_triggered = False 
    except Exception as e:
        print(f"Error in background check: {e}")
        trade_triggered = False

def on_open(ws):
    print("WebSocket Connected\n")
    payload = {"RequestCode": 17, "InstrumentCount": 1, "InstrumentList": [{"ExchangeSegment": "BSE_FNO", "SecurityId": SECURITY_ID}]}
    ws.send(json.dumps(payload))

previous_total_volume = 0

def on_message(ws, message):
    global trade_triggered, previous_total_volume

    if not isinstance(message, bytes): return

    try:
        if len(message) < 8 or message[0] != 4: return
        payload = message[8:]
        ltp = struct.unpack_from("<f", payload, 0)[0]
        last_qty = struct.unpack_from("<h", payload, 4)[0]
        timestamp = struct.unpack_from("<i", payload, 6)[0]
        total_volume = struct.unpack_from("<i", payload, 14)[0]

        # Fix: Volume calculation and early exit for redundant ticks
        if previous_total_volume == 0:
            volume_delta = total_volume if total_volume > 0 else last_qty
        else:
            volume_delta = total_volume - previous_total_volume
            if volume_delta < 0: volume_delta = last_qty
        
        # STOP processing if no new trade occurred (prevents log spam and lag)
        if volume_delta <= 0 and previous_total_volume != 0: return
        previous_total_volume = total_volume

        vwap = vwap_engine.update_tick(price=ltp, volume=volume_delta, timestamp=timestamp)
        
        # Display tick
        dt = datetime.fromtimestamp(timestamp)
        print(f"[{dt.strftime('%H:%M:%S')}] LTP: {ltp:>8.2f} | Vol: {volume_delta:>5} | VWAP: {vwap:>8.2f}")

        # Fix: Threaded signal check to prevent "ping/pong timed out"
        if not trade_triggered and vwap and abs(ltp - vwap) <= vwap_touch_threshold:
            trade_triggered = True 
            threading.Thread(target=background_signal_check, args=(ltp, vwap), daemon=True).start()

        completed_candle = candle_builder.update_tick(price=ltp, volume=volume_delta, timestamp=timestamp)
        if completed_candle:
            trade_triggered = False 
            print(f"\n{'='*20} CANDLE CLOSED {'='*20}\n")

    except Exception as e:
        print(f"Error: {e}")

def on_error(ws, error): print(f"WebSocket Error: {error}")
def on_close(ws, code, msg): print(f"WebSocket Closed: {code} {msg}")

if __name__ == "__main__":
    ws = websocket.WebSocketApp(url, on_open=on_open, on_message=on_message, on_error=on_error, on_close=on_close)
    # Ping interval keeps the connection alive
    ws.run_forever(ping_interval=20, ping_timeout=10)
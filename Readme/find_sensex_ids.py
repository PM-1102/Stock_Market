# find_sensex_ids.py
"""
Script to Download and Analyze Dhan Scrip Master File
Finds correct Security IDs for SENSEX BSE Futures and Options

FIXED VERSION: Handles actual CSV column names
"""

import requests
import pandas as pd
from datetime import datetime


def download_and_analyze_scrip_master():
    """
    Download Dhan scrip master CSV and find SENSEX-related security IDs
    """
    print("="*80)
    print("DHAN SCRIP MASTER ANALYZER - SENSEX SECURITIES")
    print("="*80)
    print()
    
    # Download URL
    url = "https://images.dhan.co/api-data/api-scrip-master-detailed.csv"
    
    print("📥 Downloading Dhan Scrip Master file...")
    print(f"   URL: {url}")
    
    try:
        # Download the CSV file
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        print("✅ Download successful!")
        print()
        
        # Save to file
        with open("dhan_scrip_master.csv", "wb") as f:
            f.write(response.content)
        
        print("💾 Saved to: dhan_scrip_master.csv")
        print()
        
        # Read CSV with pandas
        print("📊 Analyzing data...")
        df = pd.read_csv("dhan_scrip_master.csv")
        
        print(f"✅ Total instruments loaded: {len(df):,}")
        print()
        
        # 🔥 FIX: First, let's see what columns actually exist
        print("📋 Available columns in CSV:")
        print("-" * 80)
        for i, col in enumerate(df.columns, 1):
            print(f"   {i}. {col}")
        print()
        
        # 🔥 FIX: Identify the correct column names by checking common patterns
        # Common column name patterns in Dhan CSVs
        possible_symbol_cols = ['SEM_TRADING_SYMBOL', 'TRADING_SYMBOL', 'TradingSymbol', 'Symbol']
        possible_security_id_cols = ['SEM_SMST_SECURITY_ID', 'SECURITY_ID', 'SecurityId', 'security_id']
        possible_segment_cols = ['SEM_SEGMENT', 'SEGMENT', 'Segment', 'ExchangeSegment']
        possible_instrument_cols = ['SEM_INSTRUMENT_NAME', 'INSTRUMENT_NAME', 'InstrumentName']
        possible_expiry_cols = ['SEM_EXPIRY_DATE', 'EXPIRY_DATE', 'ExpiryDate', 'Expiry']
        possible_lot_cols = ['SEM_LOT_UNITS', 'LOT_SIZE', 'LotSize']
        
        def find_column(df, possible_names):
            """Find the actual column name from list of possibilities"""
            for col in possible_names:
                if col in df.columns:
                    return col
            return None
        
        # Find actual column names
        symbol_col = find_column(df, possible_symbol_cols)
        security_id_col = find_column(df, possible_security_id_cols)
        segment_col = find_column(df, possible_segment_cols)
        instrument_col = find_column(df, possible_instrument_cols)
        expiry_col = find_column(df, possible_expiry_cols)
        lot_col = find_column(df, possible_lot_cols)
        
        print("🔍 Identified column mappings:")
        print(f"   Symbol column: {symbol_col}")
        print(f"   Security ID column: {security_id_col}")
        print(f"   Segment column: {segment_col}")
        print(f"   Instrument column: {instrument_col}")
        print(f"   Expiry column: {expiry_col}")
        print(f"   Lot Size column: {lot_col}")
        print()
        
        if not all([symbol_col, security_id_col, segment_col]):
            print("❌ Error: Could not identify required columns")
            print("   Please check the CSV file manually")
            print()
            print("First 5 rows of data:")
            print(df.head())
            return df
        
        # Filter for SENSEX-related instruments
        print("="*80)
        print("FILTERING SENSEX INSTRUMENTS")
        print("="*80)
        print()
        
        # 1. Find SENSEX Index (for Option Chain)
        print("1️⃣  SENSEX INDEX (For Option Chain API)")
        print("-" * 80)
        
        # Try to find index by looking for SENSEX without FUT/OPT/CE/PE
        sensex_mask = df[symbol_col].str.contains('SENSEX', case=False, na=False)
        
        # Try to exclude futures and options
        exclude_patterns = ['FUT', 'OPT', 'CE', 'PE', 'CALL', 'PUT']
        exclude_mask = ~df[symbol_col].str.contains('|'.join(exclude_patterns), case=False, na=False)
        
        sensex_index = df[sensex_mask & exclude_mask]
        
        # If we have segment column, filter for index segment
        if segment_col and not sensex_index.empty:
            idx_segments = ['IDX_I', 'INDEX', 'IDX']
            for seg in idx_segments:
                temp = sensex_index[sensex_index[segment_col].str.contains(seg, case=False, na=False)]
                if not temp.empty:
                    sensex_index = temp
                    break
        
        if not sensex_index.empty:
            print("   Found SENSEX Index:")
            for idx, row in sensex_index.head(3).iterrows():
                print(f"\n   Security ID: {row[security_id_col]}")
                print(f"   Symbol: {row[symbol_col]}")
                if segment_col:
                    print(f"   Segment: {row[segment_col]}")
        else:
            print("   ⚠️  No clear SENSEX index found")
            print("   Showing all SENSEX instruments (may need manual verification):")
            sensex_all = df[sensex_mask].head(5)
            for idx, row in sensex_all.iterrows():
                print(f"\n   Security ID: {row[security_id_col]}")
                print(f"   Symbol: {row[symbol_col]}")
                if segment_col:
                    print(f"   Segment: {row[segment_col]}")
        
        print()
        
        # 2. Find SENSEX BSE Futures (for WebSocket)
        print("2️⃣  SENSEX BSE FUTURES (For WebSocket Live Data)")
        print("-" * 80)
        
        # Filter for SENSEX + BSE_FNO + FUTURES
        sensex_futures_mask = (
            df[symbol_col].str.contains('SENSEX', case=False, na=False) &
            df[symbol_col].str.contains('FUT', case=False, na=False)
        )
        
        # Add segment filter if available
        if segment_col:
            bse_fno_mask = df[segment_col].str.contains('BSE_FNO|BSE FNO|BSEFNO', case=False, na=False)
            sensex_futures_mask = sensex_futures_mask & bse_fno_mask
        
        sensex_futures = df[sensex_futures_mask]
        
        if not sensex_futures.empty:
            print(f"   Found {len(sensex_futures)} SENSEX Futures contracts")
            print()
            
            # Sort by expiry if column exists
            if expiry_col and expiry_col in sensex_futures.columns:
                try:
                    sensex_futures = sensex_futures.sort_values(expiry_col)
                except:
                    pass
            
            print("   📅 Available SENSEX Futures:")
            print()
            
            for idx, row in sensex_futures.head(10).iterrows():
                security_id = row[security_id_col]
                symbol = row[symbol_col]
                
                print(f"   Security ID: {security_id}")
                print(f"   Symbol: {symbol}")
                
                if segment_col:
                    print(f"   Segment: {row[segment_col]}")
                
                if expiry_col and expiry_col in row.index:
                    expiry = row[expiry_col]
                    print(f"   Expiry: {expiry}")
                    
                    # Check if this is February 2026
                    try:
                        expiry_date = pd.to_datetime(expiry)
                        if expiry_date.year == 2026 and expiry_date.month == 2:
                            print("   ⭐ THIS IS FEBRUARY 2026 CONTRACT")
                    except:
                        pass
                
                if lot_col and lot_col in row.index:
                    print(f"   Lot Size: {row[lot_col]}")
                
                print()
        else:
            print("   ⚠️  No SENSEX futures found")
            print("   Showing SENSEX + FUT combinations:")
            sensex_fut = df[df[symbol_col].str.contains('SENSEX.*FUT', case=False, na=False, regex=True)]
            for idx, row in sensex_fut.head(5).iterrows():
                print(f"\n   Security ID: {row[security_id_col]}")
                print(f"   Symbol: {row[symbol_col]}")
                if segment_col:
                    print(f"   Segment: {row[segment_col]}")
        
        print()
        
        # 3. Summary
        print("="*80)
        print("📝 CONFIGURATION SUMMARY")
        print("="*80)
        print()
        
        # Get the most likely values
        if not sensex_index.empty:
            index_id = sensex_index.iloc[0][security_id_col]
            index_symbol = sensex_index.iloc[0][symbol_col]
            
            print("✅ For Option Chain API (dhan_client.py):")
            print(f"   underlying_scrip = {index_id}")
            print(f"   Symbol: {index_symbol}")
            print()
        
        if not sensex_futures.empty:
            future_id = sensex_futures.iloc[0][security_id_col]
            future_symbol = sensex_futures.iloc[0][symbol_col]
            
            print("✅ For WebSocket Live Data (main.py):")
            print(f'   "SecurityId": "{future_id}"')
            print(f"   Symbol: {future_symbol}")
            print()
            
            # Compare with user's current ID
            if str(future_id) == "1165486":
                print("✅ Your current Future ID (1165486) matches the first contract found!")
            else:
                print(f"⚠️  First contract ID is {future_id}")
                print("   If you're using 1165486, verify it's the correct/current month")
        
        print()
        print("="*80)
        print("✅ ANALYSIS COMPLETE")
        print("="*80)
        print()
        print("📄 Full data saved to: dhan_scrip_master.csv")
        print("   You can open this in Excel to explore all instruments")
        print()
        print("💡 TIP: Look for contracts with nearest expiry date for most liquid trading")
        
        return df
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error downloading file: {e}")
        print()
        print("🔍 Troubleshooting:")
        print("   1. Check your internet connection")
        print("   2. Try accessing the URL in browser:")
        print(f"      {url}")
        print("   3. File might be temporarily unavailable")
        return None
    
    except Exception as e:
        print(f"❌ Error processing file: {e}")
        import traceback
        traceback.print_exc()
        print()
        print("💡 The CSV file has been downloaded as 'dhan_scrip_master.csv'")
        print("   You can open it in Excel and manually search for:")
        print("   - SENSEX + INDEX (for option chain)")
        print("   - SENSEX + FUT + BSE_FNO (for websocket)")
        return None


if __name__ == "__main__":
    print()
    df = download_and_analyze_scrip_master()
    
    if df is not None:
        print()
        print("="*80)
        print("MANUAL VERIFICATION (If Needed)")
        print("="*80)
        print()
        print("The CSV file 'dhan_scrip_master.csv' is now saved locally.")
        print()
        print("You can:")
        print("  1. Open it in Excel")
        print("  2. Use Ctrl+F to search for 'SENSEX'")
        print("  3. Look for:")
        print("     - Segment = 'IDX_I' (for index/option chain)")
        print("     - Segment = 'BSE_FNO' + 'FUT' in symbol (for futures)")
        print()
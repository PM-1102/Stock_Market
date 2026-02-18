import requests
import time
from datetime import datetime
from config import ACCESS_TOKEN, CLIENT_ID

class DhanClient:
    def __init__(self):
        self.base_url = "https://api.dhan.co/v2"
        
        self.last_request_time = 0
        self.rate_limit_seconds = 3  
        
    def _enforce_rate_limit(self):
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_seconds:
            sleep_time = self.rate_limit_seconds - time_since_last
            print(f"Rate limit: waiting {sleep_time:.1f}s...")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def get_expiry_list(self, underlying_scrip=51, underlying_seg="IDX_I"):
        url = f"{self.base_url}/optionchain/expirylist"
        
        headers = {
            "access-token": ACCESS_TOKEN,
            "client-id": CLIENT_ID,
            "Content-Type": "application/json"
        }
        
        payload = {
            "UnderlyingScrip": underlying_scrip,
            "UnderlyingSeg": underlying_seg
        }
        
        try:
            self._enforce_rate_limit()
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"Expiry List Error: {response.text}")
                return []
            
            data = response.json()
            if data.get("status") == "success":
                return data.get("data", [])
            else:
                print(f"Expiry List Failed: {data}")
                return []
                
        except Exception as e:
            print(f"Error fetching expiry list: {e}")
            return []


    def fetch_option_chain(self, underlying_scrip=51, underlying_seg="IDX_I", expiry=None):
        url = "https://api.dhan.co/v2/optionchain"

        headers = {
            "access-token": ACCESS_TOKEN,
            "client-id": CLIENT_ID,
            "Content-Type": "application/json"
        }

        if expiry is None:
            expiries = self.get_expiry_list(underlying_scrip, underlying_seg)
            if not expiries:
                print("No expiries found")
                return None
            expiry = expiries[0]  # Use nearest expiry
            print(f"Using nearest expiry: {expiry}")

        payload = {
            "UnderlyingScrip": underlying_scrip,
            "UnderlyingSeg": underlying_seg,
            "Expiry": expiry
        }

        try:
            self._enforce_rate_limit()
            
            response = requests.post(url, json=payload, headers=headers, timeout=15)

            if response.status_code != 200:
                print(f"Option Chain Error: {response.text}")
                return None

            data = response.json()
            
            if data.get("status") == "success":
                oc_data = data.get("data", {}).get("oc", {})
                print(f"Retrieved option chain with {len(oc_data)} strikes")
                return data
            else:
                print(f"Option Chain Failed: {data}")
                return None
                
        except Exception as e:
            print(f"Error fetching option chain: {e}")
            return None


    def get_option_chain(self, underlying_security_id=51, underlying_segment="IDX_I", expiry_date=None):
        return self.fetch_option_chain(
            underlying_scrip=underlying_security_id,
            underlying_seg=underlying_segment,
            expiry=expiry_date
        )


if __name__ == "__main__":
    print("Testing DhanClient...")
    print("=" * 60)
    
    client = DhanClient()
    
    # Test with SENSEX (Security ID: 51)
    print("\nFetching SENSEX Option Chain...")
    option_chain = client.fetch_option_chain()
    
    if option_chain:
        data = option_chain.get("data", {})
        last_price = data.get("last_price")
        oc_data = data.get("oc", {})
        
        print(f"\nSuccess!")
        print(f"   SENSEX LTP: {last_price}")
        print(f"   Total Strikes: {len(oc_data)}")
        
        # Show sample strike
        if oc_data:
            sample_strike = list(oc_data.keys())[0]
            sample_data = oc_data[sample_strike]
            
            print(f"\n   Sample Strike: {sample_strike}")
            if "ce" in sample_data:
                ce = sample_data["ce"]
                print(f"   CALL - LTP: {ce.get('last_price')}, OI: {ce.get('oi'):,}")
            if "pe" in sample_data:
                pe = sample_data["pe"]
                print(f"   PUT  - LTP: {pe.get('last_price')}, OI: {pe.get('oi'):,}")
    
    print("\n" + "=" * 60)
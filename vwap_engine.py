from datetime import datetime, time


class SessionVWAP:
    def __init__(self, session_start_hour=9, session_start_minute=15):
        self.cumulative_pv = 0.0 
        self.cumulative_volume = 0  
        self.current_vwap = None
        
        self.session_start_hour = session_start_hour
        self.session_start_minute = session_start_minute
        self.last_session_date = None
        self.session_initialized = False
        

        self.tick_count = 0
        self.last_update_time = None
    

    def update_tick(self, price, volume, timestamp):
        if self._should_reset_session(timestamp):
            self.reset_session()
            dt = datetime.fromtimestamp(timestamp)
            self.last_session_date = dt.date()
            self.session_initialized = True
            print(f"\nVWAP Session Reset at {dt.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if volume <= 0:
            return self.current_vwap
        

        pv = price * volume
        self.cumulative_pv += pv
        self.cumulative_volume += volume
        

        if self.cumulative_volume > 0:
            self.current_vwap = self.cumulative_pv / self.cumulative_volume
        

        self.tick_count += 1
        self.last_update_time = timestamp
        
        return self.current_vwap
    

    def _should_reset_session(self, timestamp):
        dt = datetime.fromtimestamp(timestamp)
        current_date = dt.date()
        current_time = dt.time()
        
        # First tick ever
        if self.last_session_date is None:
            session_start = time(self.session_start_hour, self.session_start_minute)
            if current_time >= session_start:
                return True
            return False
        
        # Check if it's a new day
        if current_date > self.last_session_date:
            session_start = time(self.session_start_hour, self.session_start_minute)
            if current_time >= session_start:
                return True
        
        return False
    
    def reset_session(self):
        self.cumulative_pv = 0.0
        self.cumulative_volume = 0
        self.current_vwap = None
        self.tick_count = 0
        self.session_initialized = True
    
    def get_vwap(self):
        return self.current_vwap
    
    def get_statistics(self):
        return {
            "vwap": self.current_vwap,
            "cumulative_pv": self.cumulative_pv,
            "cumulative_volume": self.cumulative_volume,
            "tick_count": self.tick_count,
            "session_initialized": self.session_initialized,
            "last_session_date": self.last_session_date,
            "last_update_time": datetime.fromtimestamp(self.last_update_time) if self.last_update_time else None
        }
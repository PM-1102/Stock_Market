from datetime import datetime


class CandleBuilder:

    def __init__(self):
        self.current_candle = None
        self.current_interval_start = None

    def _get_interval_start(self, timestamp):
        dt = datetime.fromtimestamp(timestamp)
        minute = (dt.minute // 5) * 5
        interval_start = dt.replace(minute=minute, second=0, microsecond=0)
        return interval_start

    def update_tick(self, price, volume, timestamp):
        interval_start = self._get_interval_start(timestamp)

        # New interval started - return completed candle
        if self.current_interval_start != interval_start:
            completed_candle = self.current_candle

            # Start new candle
            self.current_interval_start = interval_start
            self.current_candle = {
                "open": price,
                "high": price,
                "low": price,
                "close": price,
                "volume": volume,
                "start_time": interval_start
            }

            return completed_candle

        # Update current candle
        self.current_candle["high"] = max(self.current_candle["high"], price)
        self.current_candle["low"] = min(self.current_candle["low"], price)
        self.current_candle["close"] = price
        self.current_candle["volume"] += volume

        return None
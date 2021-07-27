import pandas as pd
import datetime
import alpaca
import requests
from alpaca import listeners

class SymbolCache:
    def __init__(self, symbol, cache_preload_days=20):
        self.symbol = symbol
        self.data = pd.DataFrame(
            {
                "o": [],
                "h": [],
                "l": [],
                "c": [],
                "v": []
            },
            index=[]
        )
        self.range = []
        self.listeners = {
            "1Min": [],
            "1Day": []
        }

    # makes an API call to load the data in the requested range
    def _load(self, start, end):
        response = requests.request(
            "GET",
            "https://data.alpaca.markets/v2/stocks/{0}/bars".format(self.symbol),
            headers=alpaca.HEADERS,
            params={
                "start": start.isoformat(),
                "end": end.isoformat(),
                "limit": 1000,
                "timeframe": "1Min"
            }
        )
        df = pd.DataFrame(response.json()["bars"])
        df["t"] = df["t"].apply(lambda t: datetime.datetime.fromisoformat(t.replace("Z", "+00:00")))
        df = df.set_index("t")
        self.data = self.data.append(df)

        # add the requested range to the total range
        # I really hope this works on the first try
        # TODO: date arithmetic with the market is kinda weird. create an extending class of datetime at some point
        win_index = 0
        start_win_index = -1 # -1 = not yet found
        for window in self.range:
            if start_win_index == -1:
                # start block has not yet been found
                if start < window["start"]:
                    if end < window["start"]:
                        # insert a new window
                        self.range.insert(win_index, {"start":start,"end":end})
                        break
                    elif end < window["end"]:
                        # just change the start of this window
                        window["start"] = start
                        break
                    else:
                        # begin by changing the start of this window
                        # future iterations will coalesce with other blocks as necessary
                        window["start"] = start
                        start_win_index = win_index
                else:
                    if end < window["end"]:
                        # no addition necessaary, this range already existed in the cache
                        break
                    else:
                        # this range extends past this window, possible coalescing
                        start_win_index = win_index
            else:
                # start block has been found
                if end < window["start"]:
                    # the range ends before this window
                    # change the end of the start block and coalesce as necessary
                    self.range[start_win_index]["end"] = end
                    for i in range(win_index-start_win_index-1):
                        self.range.pop(start_win_index+1)
                    break
                elif end < window["end"]:
                    # similar to the above case. spot the difference!
                    self.range[start_win_index]["end"] = end
                    for i in range(win_index-start_win_index):
                        self.range.pop(start_win_index+1)
                else:
                    # coalescing will be handled in a later iteration
                    # UNLESS this is the final iteration
                    if win_index == len(self.range)-1:
                        # same action as the above case
                        self.range[start_win_index]["end"] = end
                        for i in range(win_index-start_win_index):
                            self.range.pop(start_win_index+1)
            win_index += 1

    # TODO: complete this. I  barely started cuz it really seemed like a pain in the ass
    # takes a list of range windows and parses it into a different list of range windows based on the
    # maximum number of data points an API call can return (10000, about 25 market days of minute bars)
    # in order to minimize the number of API calls needed
    # returns the result
    def _parse_range(range):
        new_range = []
        working_range = {}
        for window in range:
            # use 35 days (5 weeks or 25 market days) as a maximum
            if window["end"] - window["start"] > datetime.timedelta(days=35):
                # this block must be split
                pass

    # returns the data in the requested range, only making an API call when needed
    def fetch(self, start, end):
        # determine if anything needs to be loaded
        bad_range = [{"start":start, "end":end}]
        # subtract good time windows from the bad range
        # NOTE: inclusive/exclusive considerations may be fucked up here...
        #       mainly because I didn't actually consider them
        #       NOTE (from future): Wow, you're lazy. So am I. Maybe next time
        for window in self.range:
            # only the last entry in bad_range can overlap with window
            # (this assumes that self.range is ordered chronologically)
            if window["end"] > bad_range[-1]["start"] and window["start"] < bad_range[-1]["end"]:
                # windows that are "inside" the range must be dealt with differentyly
                # than windows that are just "overlapping"
                # "inside": requires a split
                # "overlapping": only requires an edit
                if window["start"] > bad_range[-1]["start"]:
                    if window["end"] < bad_range[-1]["end"]:
                        # "inside"
                        bad_range.append({"start":window["end"], "end":bad_range[-1]["end"]})
                        bad_range[-2]["end"] = window["start"]
                    else:
                        # "overlapping" right
                        bad_range[-1]["end"] = window["start"]
                else:
                    # "overlapping" left
                    bad_range[-1]["start"] = window["end"]
        
        # load the missing data
        #bad_range = _parse_range(bad_range)
        for bad_window in bad_range:
            self._load(bad_window["start"], bad_window["end"])

        mask = (self.data.index >= start) & (self.data.index < end)
        return self.data.loc[mask]

    def register_listener(self, thread, timescale):
        self.listeners[timescale].append(thread)

    # notifies this cache of real time data from the alpaca socket to be stored in the cache
    def notify(self, msg):
        print(msg)
        if msg["T"] == "b":
            time = datetime.datetime.fromisoformat(msg["t"].replace("Z", "+00:00"))
            df = pd.DataFrame(
                {
                    "o": msg["o"],
                    "h": msg["h"],
                    "l": msg["l"],
                    "c": msg["c"],
                    "v": msg["v"]
                },
                index=[time] 
            )
            self.data = self.data.append(df)

            # update the range
            if len(self.range) == 0:
                self.range.append({"start": time, "end": time})
            else:
                self.range[-1]["end"] = time

            # notify all 1Min listeners
            for thread in self.listeners["1Min"]:
                thread.notify(msg)
            
            # TODO: update daily data and notify listeners when the day is over

class MarketCache:
    def __init__(self):
        self.cache = {}
        listeners.register_global_listener(self)

    def __getattr__(self, key):
        return self.get(key)

    def get(self, symbol):
        if symbol not in self.cache:
            self.cache[symbol] = SymbolCache(symbol)
        return self.cache[symbol]

    def notify(self, msg):
        self.get(msg["S"]).notify(msg)

alpaca_cache = MarketCache()
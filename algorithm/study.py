import pandas as pd
import numpy as np
import alpaca

class AdditiveStudy:
    # on_update should take a single argument: value - the newest computed value
    def __init__(self, symbol, length, on_update, timescale):
        #super().__init__(symbol)
        alpaca.alpaca_cache.get(symbol).register_listener(self, timescale)
        self.length = length
        self.timescale = timescale
        self.on_update = on_update

        self.history = [{"c":0} for i in range(length)]
        # TODO: initialize history

        self.compute() 
    
    def notify(self, msg):
        if msg["T"] == "b":
            # shift out the oldest point and shift in the new one
            self.history[:-1] = self.history[1:]
            self.history[-1] = msg
            self.compute()
            self.on_update(self.value)
    
    def compute(self):
        self.value = 0

class SimpleMovingAverage(AdditiveStudy):
    def __init__(self, symbol, length, on_update, timescale="1Min"):
        super().__init__(symbol, length, on_update, timescale)
    
    def compute(self):
        self.value = sum([p["c"] for p in self.history]) / self.length

    
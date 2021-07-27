from threading import Thread
from alpaca import listeners
from alpaca import alpaca_socket
from alpaca import alpaca_orders
import alpaca
from algorithm import study

class SymbolThread(Thread):
    MODE_LIVE = 0
    MODE_BACKTEST = 1

    def __init__(self, symbol, qty, avg_entry_price, mode=MODE_LIVE):
        super().__init__()
        self.symbol = symbol
        self.qty = qty
        self.avg_entry_price = avg_entry_price
        self.mode = mode
        self.studies = []
        self.active = False
        
        if mode == self.MODE_LIVE:
            # register self as symbol listener
            listeners.register_symbol_listener(symbol, self)

    def notify(self, message):
        pass
        # notify studies based from bars only
        # again, do I even need this?
        #if message['T'] == 'b':
        #    for study in self.studies:
        #        study.notify(message)

    # do I even need this?
    #def add_study(self, study):
    #    # TODO: initialize study
    #    self.studies.append(study)

    def run(self):
        self.active = True
        # subscribe to symbol
        alpaca_socket.send({
            "action": "subscribe",
            "bars": [self.symbol]
        })
        
        def sma9_action(value):
            print("{0}: sma9 = {1}".format(self.symbol, value))
            sma9vo = sma9v
            sma9v = value
            if sma9vo < sma20vo and sma9v >= sma20v:
                alpaca_orders.order(self.symbol, 100, "buy")
            if sma9vo > sma20vo and sma9v <= sma20v:
                alpaca_orders.order(self.symbol, 100, "sell")
        def sma20_action(value):
            print("{0}: sma20 = {1}".format(self.symbol, value))
            sma20vo = sma20v
            sma20v = value
        sma9 = study.SimpleMovingAverage(self.symbol, 9, sma9_action)
        sma20 = study.SimpleMovingAverage(self.symbol, 20, sma20_action)
        sma9v = sma9.value
        sma20v = sma20.value
        sma9vo = sma9v
        sma20vo = sma20v

        while(self.active):
            for l in alpaca.alpaca_cache.get(self.symbol).listeners:
                if l is alpaca.cache.SymbolCache:
                    print(l.length)
            pass

        alpaca_socket.send({
            "action": "unsubscribe",
            "quotes": [self.symbol]
        })
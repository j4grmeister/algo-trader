from threading import Thread
from alpaca import listeners

class SymbolThread(Thread):
    def __init__(self, symbol, qty, avg_entry_price):
        self.symbol = symbol
        listeners.register_symbol_listener(symbol, self)

    def run(self):
        pass

    def notify(self, message):
        print(message)


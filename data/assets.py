class Asset:
    #ticker
    #transactions[]

    def __init__(self, ticker):
        self.ticker = ticker
        self.transactions = []

    def add_transaction(self, type, quantity, timestamp):
        self.transactions.append(Transaction(self.ticker, type, quantity, timestamp))

class Transaction:
    def __init__(self, ticker, type, quantity, timestamp):
        pass

class Algorithm:
    #liquid
    #assets{}

    def __init__(self, budget):
        self.liquid = budget
        self.assets = {}

    def update(self):
        pass

    def buy(self):
        pass

    def sell(self):
        pass

class AlgorithmSingle(Algorithm):
    def __init__(self, ticker):
        pass

class AlgorithmMultiple(Algorithm):
    def __init__(self):
        pass

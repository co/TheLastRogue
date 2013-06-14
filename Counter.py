class Counter(object):
    def __init__(self, initValue, maxValue, minValue=0):
        if(not(minValue <= initValue <= maxValue)):
            raise Exception("Incorrectly Initialized Counter")

        self.value = initValue
        self.minValue = max(initValue, minValue)
        self.maxValue = min(initValue, maxValue)

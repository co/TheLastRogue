class Counter(object):
    def __init__(self, initValue, max_value, min_value=0):
        if(not(min_value <= initValue <= max_value)):
            raise Exception("Incorrectly Initialized Counter")

        self.__value = initValue
        self.min_value = min_value
        self.max_value = max_value

    @property
    def value(self):
        return self.__value

    def ratio_of_full(self):
        return float(self.value - self.min_value) / float(self.size())

    def size(self):
        return self.max_value - self.min_value

    def decrease(self, delta):
        self.__value = max(self.min_value, self.value - delta)

    def increase(self, delta):
        self.__value = min(self.max_value, self.value + delta)

    def set_max(self):
        self.__value = self.max_value

    def set_min(self):
        self.__value = self.min_value

class Counter(object):
    def __init__(self, init_value, max_value, min_value=0):
        if not(min_value <= init_value <= max_value):
            raise Exception("Incorrectly Initialized Counter")

        self._value = init_value
        self.min_value = min_value
        self.max_value = max_value

    @property
    def value(self):
        return self._value

    def ratio_of_full(self):
        return float(self.value - self.min_value) / float(self.size())

    def size(self):
        return self.max_value - self.min_value

    def decrease(self, delta):
        self._value = max(self.min_value, self.value - delta)

    def increase(self, delta):
        self._value = min(self.max_value, self.value + delta)

    def set_max(self):
        self._value = self.max_value

    def set_min(self):
        self._value = self.min_value

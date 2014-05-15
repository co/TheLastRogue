from compositecore import Leaf


class StatusIcon(object):
    def __init__(self, name, graphic_char):
        self.graphic_char = graphic_char
        self.name = name


class StatusBar(Leaf):
    def __init__(self):
        super(StatusBar, self).__init__()
        self.component_type = "status_bar"
        self.status_icons = []

    def clear(self):
        self.status_icons = []

    def add(self, status_icon):
        self.status_icons.append(status_icon)

    def first_tick(self, time):
        self.clear()
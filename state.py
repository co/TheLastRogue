import console


class State(object):
    def __init__(self):
        self.current_stack = None

    def update(self):
        pass

    def draw(self):
        pass


class UIState(State):
    def __init__(self, ui_element):
        super(UIState, self).__init__()
        self.ui_element = ui_element

    def draw(self):
        self.ui_element.draw()
        console.console.flush()

    def update(self):
        self.ui_element.update()

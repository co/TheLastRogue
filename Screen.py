import libtcodpy as libtcod


class Screen(object):
    def __init__(self, position, width, height, color):
        self.position = position
        self.width = width
        self.height = height
        self.color = color
        self.elements = []

    def draw(self):
        for y in range(self.position.y, self.height):
            for x in range(self.position.x, self.width + self.position.x):
                libtcod.console_set_char_background(0, x, y,
                                                    self.color)
                libtcod.console_set_char(0, x, y, ' ')

        element_position = self.position
        for element in self.elements:
            element.draw(element_position)
            element_position = element_position + (0, element.total_height)


class CounterBar(object):
    def __init__(self, counter, width, active_color,
                 inactive_color, margin_x=1, margin_y=1):
        self.counter = counter
        self.width = width
        self.active_color = active_color
        self.inactive_color = inactive_color
        self.margin_x = margin_x
        self.margin_y = margin_y
        self.total_height = 1 + margin_y * 2

    def draw(self, position):
        tiles_active = int(self.counter.ratio_of_full() * self.width)
        y = position.y + self.margin_y
        for i in range(tiles_active):
            x = position.x + i + self.margin_x
            libtcod.console_set_char(0, x, y, ' ')
            libtcod.console_set_char_background(0, x, y, self.active_color)
        for i in range(tiles_active, self.width):
            x = position.x + i + self.margin_x
            libtcod.console_set_char(0, x, y, ' ')
            libtcod.console_set_char_background(0, x, y, self.inactive_color)

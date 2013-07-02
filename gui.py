import libtcodpy as libtcod
import messenger
import math
import colors
import vector2d
import turn


class UIElement(object):
    def __init__(self, offset, width, height,
                 margin=vector2d.ZERO):
        self.offset = offset
        self.width = width
        self.height = height
        self.margin = margin
        self.elements = []

    def draw(self, offset=vector2d.ZERO):
        pass

    def update(self):
        pass

    @property
    def total_height(self):
        return self.height + self.margin.y * 2

    @property
    def total_width(self):
        return self.width + self.margin.x * 2


class StackPanel(UIElement):
    def __init__(self, offset, width, height, color_bg,
                 margin=vector2d.ZERO):
        super(StackPanel, self).__init__(offset, width, height, margin)
        self.color_bg = color_bg

    def draw(self, offset=vector2d.ZERO):
        position = offset + self.offset
        for y in range(position.y, self.height):
            for x in range(position.x, self.width + position.x):
                libtcod.console_set_char_background(0, x, y,
                                                    self.color_bg)
                libtcod.console_set_char(0, x, y, ' ')

        element_position = position
        for element in self.elements:
            element.draw(element_position)
            element_position = element_position + (0, element.total_height)


class EntityStatusList(StackPanel):
    def __init__(self, offset, width, height, color_bg):
        super(EntityStatusList, self).__init__(offset, width,
                                               height, color_bg)

    def update(self, entity):
        seen_entities = entity.get_seen_entities()
        self.elements = [EntityStatus(seen_entity,
                                      vector2d.ZERO,
                                      self.width, 3)
                         for seen_entity in seen_entities]


class EntityStatus(StackPanel):
    def __init__(self, entity, offset, width, height):
        super(EntityStatus, self).__init__(offset, width,
                                           height,
                                           colors.INTERFACE_BG)
        horizontal_margin = 0
        vertical_margin = 0
        text_height = 1
        monster_name_text_box = TextBox(entity.name[:width], vector2d.ZERO,
                                        width, text_height, colors.TEXT_ACTIVE,
                                        vector2d.Vector2D(horizontal_margin,
                                                          vertical_margin))
        monster_health_bar = CounterBar(entity.hp, self.width - 2,
                                        colors.DB_BROWN, colors.DB_LOULOU,
                                        margin=vector2d.Vector2D(1, 0))

        self.elements.append(monster_name_text_box)
        self.elements.append(monster_health_bar)


class MessageDisplay(StackPanel):
    def __init__(self, offset, width, height, color_bg):
        super(MessageDisplay, self).__init__(offset, width, height, color_bg)

    def update(self):
        messenger.messenger.push_new_messages()
        messages = messenger.messenger.tail(self.height)
        row_height = 1
        self.elements = []
        for message in messages:
            if(message.turn_created == turn.current_turn):
                color = colors.TEXT_NEW
            else:
                color = colors.TEXT_OLD
            self.elements.append(TextBox(str(message).ljust(self.width),
                                         vector2d.ZERO,
                                         self.width, row_height, color,
                                         vector2d.Vector2D(0, 0)))


class CounterBar(UIElement):
    def __init__(self, counter, width, active_color,
                 inactive_color,
                 margin=vector2d.Vector2D(1, 1),
                 offset=vector2d.ZERO):
        super(CounterBar, self).__init__(offset, width, 1, margin)
        self.counter = counter
        self.active_color = active_color
        self.inactive_color = inactive_color

    def draw(self, position=vector2d.ZERO):
        tiles_active = int(math.ceil(self.counter.ratio_of_full() *
                                     self.width))
        y = position.y + self.offset.y + self.margin.y
        x = position.x + self.offset.x + self.margin.x

        for i in range(tiles_active):
            libtcod.console_set_char(0, x + i, y, ' ')
            libtcod.console_set_char_background(0, x + i, y,
                                                self.active_color)
        for i in range(tiles_active, self.width):
            libtcod.console_set_char(0, x + i, y, ' ')
            libtcod.console_set_char_background(0, x + i, y,
                                                self.inactive_color)


class TextBox(UIElement):
    def __init__(self, text, offset, width, height,
                 text_color, margin=vector2d.Vector2D(1, 1)):
        super(TextBox, self).__init__(offset, width, height, margin)
        self.text = text
        self.text_color = text_color

    def draw(self, position=vector2d.ZERO):
        position = position + self.offset
        libtcod.console_set_default_foreground(None, self.text_color)
        libtcod.console_print(None, position.x + self.margin.x,
                              position.y + self.margin.y, self.text)

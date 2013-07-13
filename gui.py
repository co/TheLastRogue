import libtcodpy as libtcod
import messenger
import math
import colors
import vector2d
import turn


class UIElement(object):
    def __init__(self, offset, margin=vector2d.zero()):
        self.offset = offset
        self.margin = margin

    def draw(self, offset=vector2d.zero()):
        pass

    def update(self):
        pass

    @property
    def height(self):
        return 0

    @property
    def width(self):
        return 0

    @property
    def total_height(self):
        return self.height + self.margin.y * 2

    @property
    def total_width(self):
        return self.width + self.margin.x * 2


class Rectangle(UIElement):
    def __init__(self, offset, width, height, color_bg,
                 margin=vector2d.zero()):
        super(Rectangle, self).__init__(offset, margin)
        self._width = width
        self._height = height
        self.color_bg = color_bg

    @property
    def height(self):
        return self._height

    @property
    def width(self):
        return self._width

    def draw(self, offset=vector2d.zero()):
        position = offset + self.offset + self.margin
        for y in range(position.y, self.height):
            for x in range(position.x, self.width + position.x):
                libtcod.console_set_char_background(0, x, y,
                                                    self.color_bg)
                libtcod.console_set_char(0, x, y, ' ')


class RectangleGray(Rectangle):
    def __init__(self, offset, width, height, color_bg,
                 margin=vector2d.zero()):
        super(RectangleGray, self).__init__(offset, width, height,
                                            color_bg, margin)

    def draw(self, offset=vector2d.zero()):
        position = offset + self.offset + self.margin
        for y in range(position.y, self.height):
            for x in range(position.x, self.width + position.x):
                libtcod.console_set_char_background(0, x, y,
                                                    self.color_bg,
                                                    libtcod.BKGND_DARKEN)
                old_fg = 0
                libtcod.console_get_char_foreground(old_fg, x, y)
                if(old_fg == colors.UNSEEN_FG):
                    libtcod.console_set_char_foreground(0, x, y,
                                                        colors.DB_SMOKEY_ASH)
                else:
                    libtcod.console_set_char_foreground(0, x, y,
                                                        colors.
                                                        INACTIVE_GAME_FG)


class StackPanelVertical(UIElement):
    def __init__(self, offset, width, color_bg,
                 margin=vector2d.zero(), vertical_space=0):
        super(StackPanelVertical, self).__init__(offset, margin=margin)
        self._width = width
        self._horizontal_space = vertical_space
        self.color_bg = color_bg
        self.elements = []

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return sum([element.total_height for element in self.elements])

    def draw(self, offset=vector2d.zero()):
        position = offset + self.offset + self.margin

        element_position = position
        for element in self.elements:
            rectangle_bg = Rectangle(element_position, self.width,
                                     element.height, self.color_bg)
            rectangle_bg.draw()
            element.draw(element_position)
            element_position = element_position + (0, element.total_height) +\
                (0, self._horizontal_space)


class PlayerStatusBar(UIElement):
    def __init__(self, offset, width, height, color_bg, player,
                 margin=vector2d.zero()):
        super(PlayerStatusBar, self).__init__(offset, margin=margin)
        self.color_bg = color_bg
        self._status_stack_panel = StackPanelVertical(offset, width,
                                                      color_bg, margin=margin)

        name_text_box = TextBox(player.name, vector2d.zero(),
                                colors.DB_PANCHO,
                                vector2d.zero())

        description_text_box = TextBox(player.description, vector2d.zero(),
                                       colors.DB_PANCHO,
                                       vector2d.zero())

        hp_bar = CounterBar(player.hp,
                            width - 2,
                            colors.DB_BROWN, colors.DB_LOULOU)

        self._rectangle_bg = Rectangle(offset, width,
                                       height, colors.INTERFACE_BG)

        self._status_stack_panel.elements.append(name_text_box)
        self._status_stack_panel.elements.append(description_text_box)
        self._status_stack_panel.elements.append(hp_bar)

    def update(self):
        self._status_stack_panel.update()

    def draw(self, offset=vector2d.zero()):
        position = offset + self.offset + self.margin
        self._rectangle_bg.draw(position)
        self._status_stack_panel.draw(offset)


class EntityStatusList(StackPanelVertical):
    def __init__(self, offset, width, height, color_bg,
                 margin=vector2d.zero(), vertical_space=0):
        super(EntityStatusList, self).__init__(offset, width, color_bg,
                                               margin=margin,
                                               vertical_space=vertical_space)
        self._height = height
        self.rectangle_bg = Rectangle(vector2d.zero(), width,
                                      height, colors.INTERFACE_BG)

    @property
    def height(self):
        return self._height

    def update(self, entity):
        seen_entities = entity.get_seen_entities()
        self.elements = [EntityStatus(seen_entity, vector2d.zero(),
                                      self.width)
                         for seen_entity in seen_entities]

    def draw(self, offset=vector2d.zero()):
        position = offset + self.offset + self.margin
        self.rectangle_bg.draw(position)
        super(EntityStatusList, self).draw(offset)


class EntityStatus(StackPanelVertical):
    def __init__(self, entity, offset, width, margin=vector2d.zero()):
        super(EntityStatus, self).__init__(offset, width,
                                           colors.INTERFACE_BG, margin)
        monster_name_text_box = TextBox(entity.name[:width], vector2d.zero(),
                                        colors.TEXT_ACTIVE)
        monster_health_bar = CounterBar(entity.hp, self.width - 2,
                                        colors.DB_BROWN, colors.DB_LOULOU,
                                        margin=vector2d.Vector2D(1, 0))

        self.elements.append(monster_name_text_box)
        self.elements.append(monster_health_bar)


class MessageDisplay(StackPanelVertical):
    def __init__(self, offset, width, height, color_bg):
        super(MessageDisplay, self).__init__(offset, width, color_bg)
        self._height = height

    @property
    def height(self):
        return self._height

    def update(self):
        messages = messenger.messenger.tail(self.height)
        self.elements = []
        for message in messages:
            if(message.turn_created == turn.current_turn - 1):
                color = colors.TEXT_NEW
            else:
                color = colors.TEXT_OLD
            self.elements.append(TextBox(str(message).ljust(self.width),
                                         vector2d.zero(), color,
                                         vector2d.Vector2D(0, 0)))


class CounterBar(UIElement):
    def __init__(self, counter, width, active_color,
                 inactive_color,
                 margin=vector2d.Vector2D(1, 1),
                 offset=vector2d.zero()):
        super(CounterBar, self).__init__(offset, margin)
        self.counter = counter
        self.active_color = active_color
        self.inactive_color = inactive_color
        self._width = width

    @property
    def height(self):
        return 1

    @property
    def width(self):
        return self._width

    def draw(self, offset=vector2d.zero()):
        tiles_active = int(math.ceil(self.counter.ratio_of_full() *
                                     self.width))
        y = offset.y + self.offset.y + self.margin.y
        x = offset.x + self.offset.x + self.margin.x

        for i in range(tiles_active):
            libtcod.console_set_char(0, x + i, y, ' ')
            libtcod.console_set_char_background(0, x + i, y,
                                                self.active_color)
        for i in range(tiles_active, self.width):
            libtcod.console_set_char(0, x + i, y, ' ')
            libtcod.console_set_char_background(0, x + i, y,
                                                self.inactive_color)


class TextBox(UIElement):
    def __init__(self, text, offset,
                 text_color, margin=vector2d.Vector2D(0, 0)):
        super(TextBox, self).__init__(offset, margin)
        self.text = text
        self.text_color = text_color

    @property
    def height(self):
        result = self.text.count('\n') + 1
        return result

    @property
    def width(self):
        lines = self.text.split("\n")
        return max([len(line) for line in lines])

    def draw(self, position=vector2d.zero()):
        position = position + self.offset + self.margin
        libtcod.console_set_default_foreground(None, self.text_color)
        libtcod.console_print(None, position.x + self.margin.x,
                              position.y + self.margin.y, self.text)

import libtcodpy as libtcod
import messenger
import math
import colors
import geometry as geo
import turn


class UIElement(object):
    def __init__(self, margin=geo.zero2d()):
        self.margin = margin
        self.parent = None

    def draw(self, offset=geo.zero2d()):
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


class RectangularUIElement(UIElement):
    def __init__(self, rect, margin=geo.zero2d()):
        super(RectangularUIElement, self).__init__(margin)
        self.rect = rect

    @property
    def height(self):
        return self.rect.height

    @property
    def width(self):
        return self.rect.width

    @property
    def offset(self):
        return self.rect.top_left


class FilledRectangle(RectangularUIElement):
    def __init__(self, rect, color_bg, margin=geo.zero2d()):
        super(FilledRectangle, self).__init__(rect, margin)
        self.color_bg = color_bg

    def draw(self, offset=geo.zero2d()):
        position = offset + self.offset + self.margin
        for y in range(position.y, self.height + position.y):
            for x in range(position.x, self.width + position.x):
                libtcod.console_set_char_background(0, x, y, self.color_bg)
                libtcod.console_set_char(0, x, y, ' ')


class StyledRectangle(RectangularUIElement):
    def __init__(self, rect, rect_style, margin=geo.zero2d()):
        super(StyledRectangle, self).__init__(rect, margin)
        self.rect_style = rect_style

    def draw(self, offset=geo.zero2d()):
        position = offset + self.offset + self.margin
        for y in range(position.y, self.height + position.y):
            for x in range(position.x, self.width + position.x):
                char_visual = self.get_char_visual(x, y)
                StyledRectangle.draw_char(x, y, char_visual)

    def get_char_visual(self, x, y):
        if(x == self.rect.left):
            if(y == self.rect.top):
                return self.rect_style.top_left
            elif(y == self.rect.bottom - 1):
                return self.rect_style.bottom_left
            else:
                return self.rect_style.left
        if(x == self.rect.right - 1):
            if(y == self.rect.top):
                return self.rect_style.top_right
            elif(y == self.rect.bottom - 1):
                return self.rect_style.bottom_right
            else:
                return self.rect_style.right
        else:
            if(y == self.rect.top):
                return self.rect_style.top
            elif(y == self.rect.bottom - 1):
                return self.rect_style.bottom
            else:
                return self.rect_style.center

    @staticmethod
    def draw_char(x, y, char_visual):
        libtcod.console_set_char_foreground(0, x, y, char_visual.color_fg)
        libtcod.console_set_char_background(0, x, y, char_visual.color_bg)
        #if it crashes look here XXX
        libtcod.console_set_char(0, x, y, char_visual.symbol)


class RectangleGray(FilledRectangle):
    def __init__(self, rect, color_bg, margin=geo.zero2d()):
        super(RectangleGray, self).__init__(rect, color_bg, margin)

    def draw(self, offset=geo.zero2d()):
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


class UIElementSet(object):
    def __init__(self, elements):
        super(UIElementSet, self).__init__()
        self.elements = elements

    def draw(self, offset=geo.zero2d()):
        for element in self.elements:
            element.draw(offset)

    def update(self):
        for element in self.elements:
            element.update()


class StackPanelVertical(UIElement):
    def __init__(self, offset, width, margin=geo.zero2d(), vertical_space=0):
        super(StackPanelVertical, self).__init__(margin=margin)
        self._offset = offset
        self._width = width
        self.vertical_space = vertical_space
        self._elements = []

    def append(self, element):
        element.parent = self
        return self._elements.append(element)

    def clear(self):
        for element in self._elements:
            element.parent = None
        self._elements = []

    @property
    def offset(self):
        return self._offset

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return sum([element.total_height + self.vertical_space
                    for element in self._elements])

    @property
    def rectangle(self):
        return geo.Rect(self.offset, self.width, self.height)

    def update(self):
        for element in self._elements:
            element.update()

    def draw(self, offset=geo.zero2d()):
        position = offset + self.offset + self.margin

        element_position = position
        for element in self._elements:
            element.draw(element_position)
            element_position = element_position + (0, element.total_height) +\
                (0, self.vertical_space)


class PlayerStatusBar(RectangularUIElement):
    def __init__(self, rect, player, margin=geo.zero2d()):
        super(PlayerStatusBar, self).__init__(rect, margin)
        self._status_stack_panel = StackPanelVertical(self.offset, self.width,
                                                      margin=margin)

        name_text_box = TextBox(player.name, geo.zero2d(),
                                colors.DB_PANCHO,
                                geo.zero2d())

        description_text_box = TextBox(player.description, geo.zero2d(),
                                       colors.DB_PANCHO,
                                       geo.zero2d())

        hp_bar = CounterBar(player.hp, self.width - 2,
                            colors.DB_BROWN, colors.DB_LOULOU)

        self._rectangle_bg = FilledRectangle(rect, colors.INTERFACE_BG)

        self._status_stack_panel.append(name_text_box)
        self._status_stack_panel.append(description_text_box)
        self._status_stack_panel.append(hp_bar)

    def update(self):
        self._status_stack_panel.update()

    def draw(self, offset=geo.zero2d()):
        position = offset + self.offset + self.margin
        self._rectangle_bg.draw(position)
        self._status_stack_panel.draw(offset)


class EntityStatusList(StackPanelVertical):
    def __init__(self, offset, width, height,
                 margin=geo.zero2d(), vertical_space=0):
        super(EntityStatusList, self).__init__(offset, width, margin=margin,
                                               vertical_space=vertical_space)
        self._height = height
        element_bg_rect = geo.Rect(geo.zero2d(), width, height)
        self.rectangle_bg =\
            FilledRectangle(element_bg_rect, colors.INTERFACE_BG)

    @property
    def height(self):
        return self._height

    def update(self, entity):
        seen_entities = entity.get_seen_entities()
        self.clear()
        for seen_entity in seen_entities:
            self.append(EntityStatus(seen_entity, geo.zero2d(), self.width))

    def draw(self, offset=geo.zero2d()):
        position = offset + self.offset + self.margin
        self.rectangle_bg.draw(position)
        super(EntityStatusList, self).draw(offset)


class EntityStatus(StackPanelVertical):
    def __init__(self, entity, offset, width, margin=geo.zero2d()):
        super(EntityStatus, self).__init__(offset, width, margin)
        monster_name_text_box = TextBox(entity.name[:width], geo.zero2d(),
                                        colors.TEXT_ACTIVE)
        monster_health_bar = CounterBar(entity.hp, self.width - 2,
                                        colors.DB_BROWN, colors.DB_LOULOU,
                                        margin=geo.Vector2D(1, 0))

        self.append(monster_name_text_box)
        self.append(monster_health_bar)


class MessageDisplay(StackPanelVertical):
    def __init__(self, offset, width, height):
        super(MessageDisplay, self).__init__(offset, width)
        self._height = height

    @property
    def height(self):
        return self._height

    def update(self):
        messages = messenger.messenger.tail(self.height)
        self.clear()
        for message in messages:
            if(message.turn_created == turn.current_turn - 1):
                color = colors.TEXT_NEW
            else:
                color = colors.TEXT_OLD
            self.append(TextBox(str(message).ljust(self.width),
                                geo.zero2d(), color, geo.zero2d()))


class CounterBar(UIElement):
    def __init__(self, counter, width, active_color,
                 inactive_color,
                 margin=geo.Vector2D(1, 1),
                 offset=geo.zero2d()):
        super(CounterBar, self).__init__(margin)
        self.offset = offset
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

    def draw(self, offset=geo.zero2d()):
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
    def __init__(self, text, offset, text_color, margin=geo.Vector2D(0, 0)):
        super(TextBox, self).__init__(margin)
        self.offset = offset
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

    def draw(self, position=geo.zero2d()):
        position = position + self.offset + self.margin
        libtcod.console_set_default_foreground(None, self.text_color)
        libtcod.console_print(None, position.x + self.margin.x,
                              position.y + self.margin.y, self.text)

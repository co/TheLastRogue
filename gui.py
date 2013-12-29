import math
import constants
from equipment import EquipmentSlots
import frame
import graphic
import icon
import inputhandler
import inventory
from messenger import msg
from console import console
import colors
import geometry as geo
import rectfactory
import style
import settings


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
        return self.height + self.margin[1] * 2

    @property
    def total_width(self):
        return self.width + self.margin[0] * 2


class VerticalSpace(UIElement):
    def __init__(self, height, margin=geo.zero2d()):
        super(VerticalSpace, self).__init__(margin)
        self._height = height

    @property
    def height(self):
        return self._height


class HorizontalLine(UIElement):
    def __init__(self, icon, color_fg, color_bg, width, margin=geo.zero2d()):
        super(HorizontalLine, self).__init__(margin)
        self.icon = icon
        self.color_bg = color_bg
        self.color_fg = color_fg
        self._width = width

    @property
    def height(self):
        return 1

    @property
    def width(self):
        return self._width

    def draw(self, offset=geo.zero2d()):
        """
        Draws the line.
        """
        x, y = geo.add_2d(offset, self.margin)
        for i in range(self.width + 1):
            if not self.icon is None:
                console.set_symbol((x + i, y), self.icon)
            if not self.color_bg is None:
                console.set_color_bg((x + i, y), self.color_bg)
            if not self.color_fg is None:
                console.set_color_fg((x + i, y), self.color_fg)


class VerticalLine(UIElement):
    def __init__(self, graphic_char, height, margin=geo.zero2d()):
        super(VerticalLine, self).__init__(margin)
        self.graphic_char = graphic_char
        self._height = height

    @property
    def height(self):
        return self._height

    @property
    def width(self):
        return 1

    def draw(self, offset=geo.zero2d()):
        """
        Draws the line.
        """
        x, y = geo.add_2d(offset, self.margin)
        for i in range(self.height):
            if not self.graphic_char.icon is None:
                console.set_symbol((x, y + i), self.graphic_char.icon)
            if not self.graphic_char.color_bg is None:
                console.set_color_bg((x, y + i), self.graphic_char.color_bg)
            if not self.graphic_char.color_fg is None:
                console.set_color_fg((x, y + i), self.graphic_char.color_fg)


class RectangularUIElement(UIElement):
    def __init__(self, rect, margin=geo.zero2d()):
        super(RectangularUIElement, self).__init__(margin)
        self.rect = rect

    @property
    def height(self):
        return int(self.rect.height)

    @property
    def width(self):
        return int(self.rect.width)

    @property
    def offset(self):
        return geo.int_2d(self.rect.top_left)


class UIDock(RectangularUIElement):
    def __init__(self, rectangle, margin=geo.zero2d()):
        super(UIDock, self).__init__(rectangle, margin)
        self.margin = margin
        self.parent = None

        self.top = None
        self.bottom = None
        self.left = None
        self.right = None

        self.top_left = None
        self.top_right = None
        self.bottom_left = None
        self.bottom_right = None

    def draw(self, offset=geo.zero2d()):
        the_offset = geo.add_2d(offset, self.margin)
        if self.left:
            self.left.draw(geo.add_2d((0, self.height / 2 - self.left.height / 2), the_offset))
        if self.right:
            self.right.draw(geo.add_2d((self.width - self.right.width,
                                        self.height / 2 - self.right.height / 2), the_offset))
        if self.bottom:
            self.bottom.draw(geo.add_2d((self.width / 2 - self.bottom.width / 2,
                                         self.height - self.bottom.height), the_offset))
        if self.top:
            self.top.draw(geo.add_2d((1 + self.width / 2 - self.top.width / 2, 0), the_offset))
        if self.top_left:
            self.top_left.draw(the_offset)
        if self.top_right:
            self.top_right.draw(geo.add_2d((self.width - self.top_right.width, 0), the_offset))
        if self.bottom_left:
            self.bottom_left.draw(geo.add_2d((0, self.height - self.bottom_left.height), the_offset))
        if self.bottom_right:
            self.bottom_right.draw(
                geo.add_2d((self.width - self.bottom_right.width, self.height - self.bottom_right.height), the_offset))

    def update(self):
        if self.left:
            self.left.update()
        if self.right:
            self.right.update()
        if self.bottom:
            self.bottom.update()
        if self.top:
            self.top.update()

        if self.top_left:
            self.top_left.update()
        if self.top_right:
            self.top_right.update()
        if self.bottom_left:
            self.bottom_left.update()
        if self.bottom_right:
            self.bottom_right.update()


class FilledRectangle(RectangularUIElement):
    def __init__(self, rect, color_bg, margin=geo.zero2d()):
        super(FilledRectangle, self).__init__(rect, margin)
        self.color_bg = color_bg

    def draw(self, offset=geo.zero2d()):
        px, py = geo.add_2d(geo.add_2d(offset, self.offset), self.margin)
        for y in range(py, self.height + py):
            for x in range(px, self.width + px):
                console.set_color_bg((x, y), self.color_bg)
                console.set_symbol((x, y), ' ')


class StyledRectangle(RectangularUIElement):
    def __init__(self, rect, rect_style, title=None,
                 title_color_fg=colors.GRAY_D, margin=geo.zero2d()):
        super(StyledRectangle, self).__init__(rect, margin)
        self.style = rect_style
        self.title = title
        self.title_color_fg = title_color_fg

    def draw(self, offset=geo.zero2d()):
        px, py = geo.int_2d(geo.add_2d(geo.add_2d(offset, self.offset), self.margin))

        for y in range(py, self.height + py):
            for x in range(px, self.width + px):
                char_visual = self._get_char_visual(x - offset[0], y - offset[1])
                StyledRectangle.draw_char(x, y, char_visual)
        self._draw_title(offset)

    def _get_char_visual(self, x, y):
        if x == self.rect.left:
            if y == self.rect.top:
                return self.style.top_left
            elif y == self.rect.bottom - 1:
                return self.style.bottom_left
            else:
                return self.style.left
        if x == self.rect.right - 1:
            if y == self.rect.top:
                return self.style.top_right
            elif y == self.rect.bottom - 1:
                return self.style.bottom_right
            else:
                return self.style.right
        else:
            if y == self.rect.top:
                return self.style.top
            elif y == self.rect.bottom - 1:
                return self.style.bottom
            else:
                return self.style.center

    @staticmethod
    def draw_char(x, y, char_visual):
        console.set_colors_and_symbol((x, y), char_visual.color_fg,
                                      char_visual.color_bg, char_visual.icon)

    def _draw_title(self, offset=geo.zero2d()):
        if not self.title is None:
            if len(self.title) % 2 == 1:
                self.title += " "
            y = offset[1] + self.rect.top
            title_length = (self.rect.width - len(self.title) - 2)
            x_offset = self.rect.top_left[0] + title_length / 2 + offset[0]
            StyledRectangle.draw_char(x_offset, y, self.style.title_separator_left)
            x_offset += 1
            console.set_default_color_fg(self.title_color_fg)
            console.print_text((x_offset, y), self.title)
            x_offset += len(self.title)
            StyledRectangle.draw_char(x_offset, y, self.style.title_separator_right)


class RectangleChangeColor(FilledRectangle):
    def __init__(self, rect, color_bg,
                 color_fg=colors.INACTIVE_GAME_FG, margin=geo.zero2d()):
        super(RectangleChangeColor, self).__init__(rect, color_bg, margin)
        self.color_fg = color_fg

    def draw(self, offset=geo.zero2d()):
        px, py = geo.add_2d(geo.add_2d(offset, self.offset), self.margin)
        for y in range(py, self.height + py):
            for x in range(px, self.width + px):
                console.set_color_bg((x, y), self.color_bg)
                console.set_color_fg((x, y), self.color_fg)


class UIElementList(object):
    def __init__(self, elements):
        super(UIElementList, self).__init__()
        self.elements = elements

    def draw(self, offset=geo.zero2d()):
        for element in self.elements:
            element.draw(offset)

    def update(self):
        for element in self.elements:
            element.update()

    @property
    def height(self):
        if len(self.elements) < 1:
            return 0
        return max([element.height for element in self.elements])

    @property
    def width(self):
        if len(self.elements) < 1:
            return 0
        return max([element.width for element in self.elements])

    @property
    def total_width(self):
        return self.width

    @property
    def total_height(self):
        return self.height


class StackPanel(UIElement):
    def __init__(self, offset, margin=geo.zero2d()):
        super(StackPanel, self).__init__(margin=margin)
        self._offset = offset
        self.elements = []

    def append(self, element):
        element.parent = self
        return self.elements.append(element)

    def clear(self):
        for element in self.elements:
            element.parent = None
        self.elements = []

    @property
    def offset(self):
        return self._offset

    @property
    def rectangle(self):
        return geo.Rect(self.offset, self.width, self.height)

    def update(self):
        for element in self.elements:
            element.update()


class StackPanelHorizontal(StackPanel):
    ALIGN_TOP = 0
    ALIGN_CENTER = 1
    ALIGN_BOTTOM = 2

    def __init__(self, offset, margin=geo.zero2d(), horizontal_space=0, alignment=ALIGN_TOP):
        super(StackPanelHorizontal, self).__init__(offset, margin=margin)
        self.horizontal_space = horizontal_space
        self.alignment = alignment

    @property
    def height(self):
        if len(self.elements) < 1:
            return 0
        return max([element.total_height for element in self.elements])

    @property
    def width(self):
        return (sum([element.total_width for element in self.elements])
                + max(self.horizontal_space * (len(self.elements) - 1), 0))

    def draw(self, offset=geo.zero2d()):
        position = geo.add_2d(geo.add_2d(offset, self.offset), self.margin)
        element_position = position
        for element in self.elements:
            element.draw(geo.add_2d((0, self.get_y_offset(element)), element_position))
            element_position = geo.add_2d(element_position, (element.total_width + self.horizontal_space, 0))


    def get_y_offset(self, element):
        if self.alignment == StackPanelHorizontal.ALIGN_TOP:
            return 0
        elif self.alignment == StackPanelHorizontal.ALIGN_CENTER:
            return (self.height - element.height + 1) / 2
        elif self.alignment == StackPanelHorizontal.ALIGN_BOTTOM:
            return self.height - element.height


class StackPanelVertical(StackPanel):
    ALIGN_LEFT = 0
    ALIGN_CENTER = 1
    ALIGN_RIGHT = 2

    def __init__(self, offset, margin=geo.zero2d(), vertical_space=0, alignment=ALIGN_LEFT):
        super(StackPanelVertical, self).__init__(offset, margin=margin)
        self.vertical_space = vertical_space
        self.alignment = alignment

    @property
    def width(self):
        if len(self.elements) < 1:
            return 0
        return max([element.total_width for element in self.elements])

    @property
    def height(self):
        return (sum([element.total_height for element in self.elements])
                + max(self.vertical_space * (len(self.elements) - 1), 0))

    def draw(self, offset=geo.zero2d()):
        position = geo.add_2d(geo.add_2d(offset, self.offset), self.margin)
        element_position = position
        for element in self.elements:
            element.draw(geo.add_2d((self.get_x_offset(element), 0), element_position))
            element_position = geo.add_2d(element_position, (0, element.total_height + self.vertical_space))

    def get_x_offset(self, element):
        if self.alignment == StackPanelVertical.ALIGN_LEFT:
            return 0
        elif self.alignment == StackPanelVertical.ALIGN_CENTER:
            return (self.width - element.width + 1) / 2 - 1
        elif self.alignment == StackPanelVertical.ALIGN_RIGHT:
            return self.width - element.width


class CommandListPanel(UIElement):
    def __init__(self, margin=geo.zero2d()):
        super(CommandListPanel, self).__init__(margin)
        self._pages = []
        self._pages.append(StackPanelVertical(geo.add_2d((0, 0), (2, 2)), vertical_space=0))
        self._pages.append(StackPanelVertical(geo.add_2d((0, 0), (2, 2)), vertical_space=0))
        self.active = True
        self.current_page_index = 0

        self._bg_rect = StyledRectangle(rectfactory.command_list_rectangle(),
                                        style.MinimalClassicStyle2(), title="Commands")

        self._pages[0].append(self.left_right_adjust("Walk", "Mouse/Numpad"))
        self._pages[0].append(self.left_right_adjust("Pick Up/Use", "Space/" + str(settings.KEY_USE_PICK_UP), colors.LIGHT_PINK))
        self._pages[0].append(self.left_right_adjust("Explore", settings.KEY_AUTO_EXPLORE, colors.LIGHT_GREEN))
        self._pages[0].append(self.left_right_adjust("Fire/Throw", settings.KEY_FIRE))
        self._pages[0].append(self.left_right_adjust("Wait/Rest", settings.KEY_REST))
        self._pages[0].append(self.left_right_adjust("Inventory", settings.KEY_INVENTORY))
        self._pages[0].append(self.left_right_adjust("Equipment", settings.KEY_EQUIPMENT))
        self._pages[0].append(VerticalSpace(1))
        self._pages[0].append(self.left_right_adjust("Print Screen", "F12"))
        self._pages[0].append(self.left_right_adjust("Save/Quit", "Esc"))
        self._pages[0].append(VerticalSpace(1))
        self._pages[0].append(self.left_right_adjust("Next Page", "Tab", colors.LIGHT_ORANGE))

        self._pages[1].append(self.left_right_adjust("Examine", settings.KEY_EXAMINE))
        self._pages[1].append(self.left_right_adjust("Wear/Wield", settings.KEY_WEAR_WIELD))
        self._pages[1].append(self.left_right_adjust("Drink Potion", settings.KEY_DRINK))
        self._pages[1].append(VerticalSpace(self._bg_rect.height - self._pages[1].height - 5))
        self._pages[1].append(self.left_right_adjust("Next Page", "Tab", colors.LIGHT_ORANGE))

        text = "Press Tab"
        offset = (self._pages[0].width + 4, (self.height - len(text)) / 2)
        self._inactive_text = VerticalTextBox(text, offset, colors.LIGHT_ORANGE)

        self._inactive_line = VerticalLine(graphic.GraphicChar(colors.INTERFACE_BG, colors.GRAY_D, icon.V_LINE),
                                           self.height, (self.width - 1, 0))

    @property
    def height(self):
        return self._bg_rect.height

    @property
    def width(self):
        return self._bg_rect.width

    def left_right_adjust(self, text1, text2, color=colors.GRAY):
        return TextBox(text1 + text2.rjust(constants.RIGHT_SIDE_BAR_WIDTH - len(text1) - 5), (0, 0), color)

    def draw(self, offset=geo.zero2d()):
        if self.current_page_index == - 1:
            self._inactive_line.draw(offset)
            self._inactive_text.draw(offset)
        else:
            self._bg_rect.draw(offset)
            self._pages[self.current_page_index].draw(offset)

    def turn_page(self):
        if self.current_page_index < len(self._pages) - 1:
            print self.current_page_index
            self.current_page_index += 1
        else:
            print "yy", self.current_page_index
            self.current_page_index = - 1


class PlayerStatusBox(RectangularUIElement):
    def __init__(self, rect, player, margin=geo.zero2d()):
        super(PlayerStatusBox, self).__init__(rect, margin)
        self._player = player
        self._status_stack_panel = StackPanelVertical(rect.top_left, (1, 2))

        element_width = self.width - style.interface_theme.margin[0] * 2 - 2
        player_hp = player.health.hp
        hp_bar = CounterBarWithNumbers(player_hp, element_width, colors.HP_BAR_FULL, colors.HP_BAR_EMPTY,
                                       colors.WHITE, colors.PINK, colors.HP_BAR_EMPTY, colors.CYAN, colors.BLACK)
        heart = SymbolUIElement((0, 0), graphic.GraphicChar(None, colors.RED, icon.HEALTH_STAT))

        self._hp_stack_panel = StackPanelHorizontal((0, 0), (0, 1), 1)
        self._hp_stack_panel.append(heart)
        self._hp_stack_panel.append(hp_bar)

        self._rectangle_bg = StyledRectangle(rect, style.interface_theme.rect_style,
                            player.description.name, player.graphic_char.color_fg)

        self._status_stack_panel.append(self._hp_stack_panel)
        inner_margin = 3
        item_row_height = 6
        dock = UIDock(geo.Rect((0, 0), self.width - inner_margin * 2, item_row_height), margin=(2, 1))

        dock.bottom_left = InventoryBox(player.inventory, item_row_height - 2)
        dock.bottom_right = EquipmentBox(player.equipment, geo.Rect((0, 0), 5, 6))
        self._status_stack_panel.append(dock)

        self.depth_text_box = TextBox("", (2, 0), colors.CYAN_D)
        self._status_stack_panel.append(self.depth_text_box)

    @property
    def height(self):
        return self.rect.height

    @property
    def width(self):
        return self.rect.width

    def update(self):
        self._status_stack_panel.update()
        self.depth_text_box.text = ("Depth:" + str(self._player.dungeon_level.value.depth + 1).rjust(2))

    def draw(self, offset=geo.zero2d()):
        position = geo.add_2d(offset, self.margin)
        self._rectangle_bg.draw(position)
        self._status_stack_panel.draw(position)


class EquipmentBox(RectangularUIElement):
    POSITIONS = {EquipmentSlots.HEADGEAR: (2, 1),
                 EquipmentSlots.LEFT_RING: (1, 2),
                 EquipmentSlots.AMULET: (2, 2),
                 EquipmentSlots.RIGHT_RING: (3, 2),
                 EquipmentSlots.MELEE_WEAPON: (1, 3),
                 EquipmentSlots.ARMOR: (2, 3),
                 EquipmentSlots.RANGED_WEAPON: (3, 3),
                 EquipmentSlots.BOOTS: (2, 4)}

    def __init__(self, equipment, rect, margin=geo.zero2d()):
        super(EquipmentBox, self).__init__(rect, margin=margin)
        self._equipment = equipment
        self._bg_rect = StyledRectangle(rect, style.MinimalStyle())
        self._equipment_slot_items = []

    def update(self):
        self._equipment_slot_items = []
        for slot in EquipmentSlots.ALL:
            if self._equipment.slot_is_equiped(slot):
                item = self._equipment.get(slot)
                graphic_item = SymbolUIElement(EquipmentBox.POSITIONS[slot], item.graphic_char)
            else:
                graphic_item = SymbolUIElement(EquipmentBox.POSITIONS[slot],
                                               graphic.GraphicChar(None, colors.NOT_EQUIPPED_FG, slot.icon))
            self._equipment_slot_items.append(graphic_item)

    def draw(self, offset=geo.zero2d()):
        position = geo.add_2d(offset, self.margin)
        self._bg_rect.draw(position)

        for graphic_item in self._equipment_slot_items:
            graphic_item.draw(position)


class InventoryBox(RectangularUIElement):
    def __init__(self, the_inventory, height, margin=geo.zero2d()):
        super(InventoryBox, self).__init__(geo.Rect((0, 0), inventory.ITEM_CAPACITY / height + 2, height + 2),
                                           margin=margin)
        self._inventory = the_inventory
        self._inventory_height = self.rect.height - 2
        self._inventory_width = self.rect.width - 2
        self._bg_rect = StyledRectangle(self.rect, style.ChestStyle())
        self.graphic_char_items = []

    def update(self):
        items = self._inventory.get_items_sorted()
        self.graphic_char_items = []
        for idx, item in enumerate(items):
            offset = (idx % self._inventory_width, idx / self._inventory_width)
            graphic_item = SymbolUIElement(offset, item.graphic_char)
            self.graphic_char_items.append(graphic_item)

    def draw(self, offset=geo.zero2d()):
        position = geo.add_2d(offset, self.margin)
        self._bg_rect.draw(position)
        for graphic_item in self.graphic_char_items:
            graphic_item.draw(geo.add_2d(position, (1, 1)))


class EntityStatusList(UIElement):
    def __init__(self, looking_entity, width, margin=geo.zero2d(), vertical_space=0):
        super(EntityStatusList, self).__init__(margin=margin)
        self._entity_stack_panel = StackPanelVertical((0, 0), (0, 0), vertical_space=vertical_space)
        self.looking_entity = looking_entity
        self._width = width

    def update(self):
        seen_entities = self.looking_entity.vision.get_seen_entities_closest_first()
        seen_entities.reverse()
        if self.looking_entity in seen_entities:
            seen_entities.remove(self.looking_entity)
        self._entity_stack_panel.clear()
        rect = geo.Rect((0, 0), self.width, 3)
        for seen_entity in seen_entities:
            entity_status = EntityStatus(seen_entity, rect)
            self._entity_stack_panel.append(entity_status)

    def draw(self, offset=geo.zero2d()):
        self._entity_stack_panel.draw(geo.add_2d(offset, self.margin))

    @property
    def height(self):
        return self._entity_stack_panel.height

    @property
    def width(self):
        return self._width


class EntityStatus(UIElement):
    def __init__(self, entity, rect, margin=geo.zero2d()):
        super(EntityStatus, self).__init__(margin)
        self._width = rect.width
        element_width = self.width - style.interface_theme.margin[0] * 2 - 2
        monster_health_bar = CounterBar(entity.health.hp, element_width,
                                        colors.HP_BAR_FULL,
                                        colors.HP_BAR_EMPTY)

        entity_symbol = SymbolUIElement((0, 0), entity.graphic_char)

        self._hp_stack_panel = StackPanelHorizontal((0, 0), (1, 1), 1)
        self._hp_stack_panel.append(entity_symbol)
        self._hp_stack_panel.append(monster_health_bar)

        self._rectangle_bg = StyledRectangle(rect, style.monster_list_card,
                                             entity.description.name, entity.graphic_char.color_fg)

        self._status_stack_panel = StackPanelVertical(rect.top_left, margin)
        self._status_stack_panel.append(self._hp_stack_panel)

    @property
    def height(self):
        return self._status_stack_panel.height

    @property
    def width(self):
        return self._width

    def draw(self, offset=geo.zero2d()):
        offset = geo.add_2d(offset, self.margin)
        self._rectangle_bg.draw(offset)
        self._status_stack_panel.draw(offset)


class DescriptionCard(RectangularUIElement):
    """
    GUI Element for displaying a description object as text in a styled rectangle.
    """
    def __init__(self, rect, gui_style, heading_fg=colors.WHITE, margin=(0, 0), vertical_space=1):
        super(DescriptionCard, self).__init__(rect, margin=margin)
        self._bg_rect = StyledRectangle(self.rect, gui_style.rect_style)
        self.text_stack_panel = StackPanelVertical(gui_style.margin, vertical_space=vertical_space,
                                                   alignment=StackPanelVertical.ALIGN_LEFT)
        self.description = None
        self.heading_fg = heading_fg
        self._inner_margin = gui_style.margin
        self._offset = (0, 0)

    def update(self):
        self.text_stack_panel.clear()
        if self.description:
            self.text_stack_panel.append(TextBox(self.description.name, (0, 0), self.heading_fg))
            self.text_stack_panel.append(TextBoxWrap(self.description.description, (0, 0), colors.WHITE,
                                                     self.width - self._inner_margin[0] - 1,
                                                     self.height - self._inner_margin[1]))

    def draw(self, offset=geo.zero2d()):
        if self.description:
            position = geo.int_2d(geo.add_2d(geo.add_2d(offset, self.offset), self.margin))
            self._bg_rect.draw(position)
            self.text_stack_panel.draw(position)


class MessageDisplay(RectangularUIElement):
    def __init__(self, rect, margin=(0, 0), vertical_space=0):
        super(MessageDisplay, self).__init__(rect, margin=margin)
        self._message_stack_panel = StackPanelVertical(rect.top_left, margin=style.interface_theme.margin,
                                                       vertical_space=vertical_space)
        self._offset = (0, 0)

    def update(self):
        if msg.has_new_message:
            messages_height = (self.height - style.interface_theme.margin[0] * 2)
            messages = msg.tail(messages_height)
            self._message_stack_panel.clear()
            for message in messages:
                message_width = (self.width - style.interface_theme.margin[0] * 2)
                words = str(message).split()
                lines = []
                line = words[0]
                for word in words[1:]:
                    if len(line) + len(" " + word) > message_width:
                        lines.append(line)
                        line = word
                    else:
                        line += (" " + word)

                if len(line) >= 1:
                    lines.append(line)
                for line in lines:
                    text_box = TextBox(str(line), geo.zero2d(), colors.TEXT_OLD, geo.zero2d())
                    self._message_stack_panel.append(text_box)
                self._offset = (0, constants.GUI_BOX_HEIGHT - self._message_stack_panel.height - 4)

    def draw(self, offset=geo.zero2d()):
        offset = geo.add_2d(offset, self._offset)
        self._message_stack_panel.draw(offset)


class CounterBar(UIElement):
    """
    Draws a bar showing the ratio between the current and max value of counter.
    """

    def __init__(self, counter, width, active_color, inactive_color,
                 inc_color=None, dec_color=None, max_inc_color=None, max_dec_color=None,
                 margin=(0, 0), offset=geo.zero2d()):
        super(CounterBar, self).__init__(margin)
        self.offset = offset
        self.counter = counter
        self._width = width

        self.active_color = active_color
        self.inactive_color = inactive_color

        self.inc_color = inc_color
        self.dec_color = dec_color
        self.max_inc_color = max_inc_color
        self.max_dec_color = max_dec_color

        self.last_value = self.counter.value
        self.last_max_value = self.counter.max_value

    @property
    def height(self):
        return 1

    @property
    def width(self):
        return self._width

    def draw(self, offset=geo.zero2d()):
        """
        Draws the bar.
        """
        self._draw_bar(self._get_active_color(), self.inactive_color, offset)

    def _get_active_color(self):
        if self.last_max_value < self.counter.max_value:
            self.last_max_value = self.counter.max_value
            return self.max_inc_color
        elif self.last_max_value > self.counter.max_value:
            self.last_max_value = self.counter.max_value
            return self.max_dec_color
        elif self.last_value < self.counter.value:
            self.last_value = self.counter.value
            return self.inc_color
        elif self.last_value > self.counter.value:
            self.last_value = self.counter.value
            return self.dec_color
        else:
            return self.active_color

    def _draw_bar(self, active_color, inactive_color, offset=geo.zero2d()):
        """
        Draws the bar.
        """
        tiles_active = int(math.ceil(self.counter.ratio_of_full() *
                                     self.width))
        x, y = geo.add_2d(geo.add_2d(offset, self.offset), self.margin)
        for i in range(tiles_active):
            console.set_symbol((x + i, y), ' ')
            console.set_color_bg((x + i, y), active_color)
        for i in range(tiles_active, self.width):
            console.set_symbol((x + i, y), ' ')
            console.set_color_bg((x + i, y), inactive_color)


class CounterBarWithNumbers(CounterBar):
    """
    Will display current and max value of counter on the bar.
    """

    def __init__(self, counter, width, active_color, inactive_color, text_color,
                 inc_color=None, dec_color=None, max_inc_color=None, max_dec_color=None,
                 margin=(0, 0), offset=geo.zero2d()):
        super(CounterBarWithNumbers, self).__init__(counter, width,
                                                    active_color,
                                                    inactive_color,
                                                    inc_color, dec_color, max_inc_color, max_dec_color,
                                                    margin, offset)
        self.text_color = text_color

    def draw(self, offset=geo.zero2d()):
        """
        Draws the bar with numbers.
        """
        self._draw_bar(self._get_active_color(), self.inactive_color, offset)
        console.set_default_color_fg(self.text_color)
        self._draw_numbers(offset)

    def _draw_numbers(self, offset):
        """
        Draws the numbers.
        """
        x, y = geo.add_2d(geo.add_2d(offset, self.offset), self.margin)
        text = (str(self.counter.value) +
                " (" + str(self.counter.max_value) + ")")
        x_offset = (self.width - len(text)) / 2
        position = (x + x_offset, y)

        console.print_text(position, text)


class TextBox(UIElement):
    def __init__(self, text, offset, color_fg, margin=(0, 0)):
        super(TextBox, self).__init__(margin)
        self.offset = offset
        self.text = text
        self.color_fg = color_fg

    @property
    def height(self):
        result = self.text.count('\n') + 1
        return result

    @property
    def width(self):
        lines = self.text.split("\n")
        return max([len(line) for line in lines])

    def draw(self, offset=geo.zero2d()):
        x, y = geo.int_2d(geo.add_2d(geo.add_2d(offset, self.offset), self.margin))
        if x > settings.SCREEN_WIDTH:
            return
        if x + len(self.text) > settings.SCREEN_WIDTH:
            max_width = settings.SCREEN_WIDTH - x
            show_text = self.text[:max_width - 3] + "..."
        else:
            show_text = self.text

        console.set_default_color_fg(self.color_fg)
        console.print_text((x, y), show_text)


class TextBoxWrap(UIElement):
    def __init__(self, text, offset, color_fg, row_max_width, max_rows, margin=(0, 0), vertical_space=0):
        super(TextBoxWrap, self).__init__(margin)
        self.offset = offset
        self.text = text
        self.color_fg = color_fg
        self.row_max_width = row_max_width
        self.max_rows = max_rows
        self._text_stack_panel = StackPanelVertical(offset, (0, 0), vertical_space=vertical_space)

    def update(self):
        words = str(self.text).split()
        lines = []
        line = words[0]
        for word in words[1:]:
            if len(line) + len(" " + word) > self.row_max_width:
                lines.append(line)
                line = word
            else:
                line += (" " + word)
        if len(line) >= 1:
            lines.append(line)
        for line in lines:
            text_box = TextBox(str(line), (0, 0), self.color_fg, (0, 0))
            self._text_stack_panel.append(text_box)

    def draw(self, offset=geo.zero2d()):
        self.update()
        position = geo.int_2d(geo.add_2d(geo.add_2d(offset, self.offset), self.margin))
        self._text_stack_panel.draw(position)


class VerticalTextBox(UIElement):
    def __init__(self, text, offset, color_fg, margin=(0, 0)):
        super(VerticalTextBox, self).__init__(margin)
        self.offset = offset
        self.text = text
        self.color_fg = color_fg

    @property
    def height(self):
        return len(self.text)

    @property
    def width(self):
        return 1

    def draw(self, offset=geo.zero2d()):
        x, y = geo.int_2d(geo.add_2d(geo.add_2d(offset, self.offset), self.margin))
        console.set_default_color_fg(self.color_fg)
        console.print_text_vertical((x, y), self.text)


class SymbolUIElement(UIElement):
    def __init__(self, offset, graphic_char, margin=(0, 0)):
        super(SymbolUIElement, self).__init__(margin)
        self.offset = offset
        self.graphic_char = graphic_char

    @property
    def height(self):
        return 1

    @property
    def width(self):
        return 1

    def draw(self, offset=geo.zero2d()):
        x, y = geo.int_2d(geo.add_2d(geo.add_2d(offset, self.offset), self.margin))
        if not self.graphic_char.color_fg is None:
            console.set_color_fg((x, y), self.graphic_char.color_fg)
        if not self.graphic_char.color_bg is None:
            console.set_color_bg((x, y), self.graphic_char.color_bg)
        console.set_symbol((x, y), self.graphic_char.icon)


class TypeWriter(UIElement):
    """
    Takes alphanumerical input and prints the text on screen.
    Assumes it is used together with a menu which updates the inputhandler.
    """

    def __init__(self, offset, active_color_fg, inactive_color_fg, max_length, default_text="", color_bg=None, margin=(0, 0)):
        super(TypeWriter, self).__init__(margin)
        self.offset = offset
        self.active_color_fg = active_color_fg
        self.inactive_color_fg = inactive_color_fg
        self.color_bg = color_bg
        self._text = TextBox(default_text[:max_length], (0, 0), active_color_fg)
        self._text_cursor = SymbolUIElement((0, 0), graphic.GraphicChar(None, active_color_fg, '_'))
        self._text_line = StackPanelHorizontal((0, 0))
        self._text_line.append(self._text)
        self._text_line.append(self._text_cursor)
        self.max_length = max_length
        self.any_key_pressed_yet = False
        self.is_active = True
        self.update_text_look()

    @property
    def height(self):
        return self._text.height

    @property
    def width(self):
        return self._text.width

    @property
    def text(self):
        return self._text.text

    def update_text_look(self):
        self._text.color_fg = self.active_color_fg if self.is_active else self.inactive_color_fg
        animation_length = 8
        current_animation_frame = frame.current_frame % (animation_length * 2)
        if self.is_active and current_animation_frame > animation_length:
            self._text_cursor.graphic_char.color_fg = self.active_color_fg
        else:
            self._text_cursor.graphic_char.color_fg = self.inactive_color_fg

    def update(self):
        self.update_text_look()

        key = inputhandler.handler.get_keypress_char()
        special_key = inputhandler.handler.get_keypress()
        if ((not key is None) and key in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
            and len(self._text.text) < self.max_length):
            self.clear_if_first_key_press()
            self._text.text += key
        if (special_key == inputhandler.BACKSPACE or special_key == inputhandler.DELETE) and len(self._text.text) > 0:
            self.clear_if_first_key_press()
            self._text.text = self._text.text[:-1]

    def draw(self, offset=geo.zero2d()):
        draw_offset = geo.add_2d(geo.add_2d(offset, self.offset), self.margin)
        self._text_line.draw(draw_offset)

    def clear_if_first_key_press(self):
        if not self.any_key_pressed_yet:
            self._text.text = ""
            self.any_key_pressed_yet = True


class UpdateCallOnlyElement(UIElement):
    def __init__(self, update_functions):
        self.update_functions = update_functions

    def update(self):
        for function in self.update_functions:
            function()


class InfoTextLine(UIElement):
    def __init__(self, texts, color_bg=colors.DARK_GREEN, color_fg=colors.GREEN,
                 width=settings.SCREEN_WIDTH, margin=geo.zero2d()):
        super(InfoTextLine, self).__init__(margin)
        self.margin = margin
        self.parent = None
        self.texts = texts
        self.color_bg = color_bg
        self.color_fg = color_fg
        self._width = width
        if settings.MINIMUM_WIDTH < max(len(text) for text in texts):
            raise Exception("Info texts is longer than minimum resolution.")
        if constants.MAX_INFO_LINES < len(texts):
            raise Exception("Info texts is longer than minimum resolution.")
        self._text_stack_panel = StackPanelVertical((0, 0), alignment=StackPanelVertical.ALIGN_CENTER)
        self._bg_stack_panel = StackPanelVertical((0, 0), alignment=StackPanelVertical.ALIGN_CENTER)
        self.dock = UIDock(rectfactory.full_screen_rect())
        self.update()

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return 1

    def update(self):
        self._text_stack_panel.clear()
        self._bg_stack_panel.clear()
        for text in self.texts:
            self._text_stack_panel.append(TextBox(text, (0, 0), self.color_fg))
            self._bg_stack_panel.append(HorizontalLine(" ", self.color_fg, self.color_bg, self.width))
        self.dock.top = UIElementList([self._text_stack_panel])

    def draw(self):
        self._bg_stack_panel.draw()
        self.dock.draw()

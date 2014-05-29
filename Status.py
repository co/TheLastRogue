import colors
from compositecore import Leaf
from graphic import GraphicChar
import icon


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

FIRE_STATUS_ICON = StatusIcon("Fire", GraphicChar(None, colors.RED, icon.FIRE))
POISON_STATUS_ICON = StatusIcon("Poison", GraphicChar(None, colors.GREEN, icon.POTION))
STUNNED_STATUS_ICON = StatusIcon("Stunned", GraphicChar(None, colors.CHAMPAGNE, "*"))
DAMAGE_REFLECT_STATUS_ICON = StatusIcon("Damage Reflect", GraphicChar(None, colors.CYAN, icon.ARMOR_STAT))
LIFE_STEAL_STATUS_ICON = StatusIcon("Life Steal", GraphicChar(None, colors.RED, "V"))
STUMBLE_STATUS_ICON = StatusIcon("Stumble", GraphicChar(None, colors.YELLOW, "+"))

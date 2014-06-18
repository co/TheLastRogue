import colors
from compositecore import Leaf
from graphic import GraphicChar
import icon


class StatusDescription(object):
    def __init__(self, name, graphic_char, description):
        self.graphic_char = graphic_char
        self.name = name
        self.description = description


class StatusDescriptionBar(Leaf):
    def __init__(self):
        super(StatusDescriptionBar, self).__init__()
        self.component_type = "status_bar"
        self.statuses = []

    def clear(self):
        self.statuses = []

    def add(self, status_icon):
        self.statuses.append(status_icon)

    def first_tick(self, time):
        self.clear()

FIRE_STATUS_DESCRIPTION = StatusDescription("Fire", GraphicChar(None, colors.RED, icon.FIRE), "You are standing in flames, taking heavy fire damage each turn spent in the flames.")
POISON_STATUS_DESCRIPTION = StatusDescription("Poison", GraphicChar(None, colors.GREEN, icon.POTION), "Poisoned, while poisoned you will take poison damage, the poison will wear off after a while.")
STUNNED_STATUS_DESCRIPTION = StatusDescription("Stunned", GraphicChar(None, colors.CHAMPAGNE, "*"), "You are stunned and will skip your next turn.")
DAMAGE_REFLECT_STATUS_DESCRIPTION = StatusDescription("Damage Reflect", GraphicChar(None, colors.CYAN, icon.ARMOR_STAT), "When you take damage there is a chance that each enemy you see will take one point of damage.")
LIFE_STEAL_STATUS_DESCRIPTION = StatusDescription("Life Steal", GraphicChar(None, colors.RED, "V"), "When an enemy dies within sight you will heal one point of health.")
STUMBLE_STATUS_DESCRIPTION = StatusDescription("Stumble", GraphicChar(None, colors.YELLOW, "+"), "Your next step will be in a random direction.")
SLEEP_STATUS_DESCRIPTION = StatusDescription("Sleeping", GraphicChar(None, colors.GRAY, "Z"), "You will be unable to do anything until you take damage.")

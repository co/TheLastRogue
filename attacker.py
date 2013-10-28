import damage
from compositecore import Leaf


class Attacker(Leaf):
    """
    Component for moving and checking if a move is legal.
    """
    def __init__(self):
        super(Attacker, self).__init__()
        self.component_type = "attacker"

    def try_hit(self, position):
        """
        Tries to hit an entity at a position.

        Returns False if there is no entity
        there or the entity is of the same faction.
        """
        entity = (self.parent.dungeon_level.value.
                  get_tile(position).get_first_entity())
        if(entity is None or
           entity.faction.value == self.parent.faction.value):
            return False
        self.hit(entity)
        return True

    def throw_rock_damage_entity(self, target_entity):
        """
        Makes entity to hit the target entity with the force of a thrown rock.
        """
        damage_types = [damage.DamageTypes.BLUNT, damage.DamageTypes.PHYSICAL]
        strength = self.parent.strength.value
        thrown_damage = damage.Damage(strength / 2, strength / 3, damage_types)
        thrown_damage.damage_entity(self.parent, target_entity)

    def hit(self, target_entity):
        """
        Causes the entity to hit the target entity.
        """
        # implement melee weapon damage here.
        self._unarmed_damage().damage_entity(self.parent, target_entity)

    def _unarmed_damage(self):
        """
        Calculates an instance of damage
        caused by an unarmed hit by the entity.
        """
        damage_types = [damage.DamageTypes.BLUNT, damage.DamageTypes.PHYSICAL]
        strength = self.parent.strength.value
        return damage.Damage(strength, strength / 2, damage_types)

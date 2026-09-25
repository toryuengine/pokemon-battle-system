from ability.base_ability import BaseAbility

TECHNICIAN_POWER_THRESHOLD = 60
TECHNICIAN_MULTIPLIER = 1.5


# テクニシャン: 威力60以下の技の威力が1.5倍
class Technician(BaseAbility):
    def __init__(self):
        super().__init__(id=42)

    def get_power_multiplier(self, attacker, move, power) -> float:
        if power <= TECHNICIAN_POWER_THRESHOLD:
            return TECHNICIAN_MULTIPLIER
        return 1.0

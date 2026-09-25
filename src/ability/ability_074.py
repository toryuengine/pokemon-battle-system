from ability.base_ability import BaseAbility

TINTED_LENS_MULTIPLIER = 2.0


# いろめがね: 効果がいまひとつの技のダメージが2倍
class TintedLens(BaseAbility):
    def __init__(self):
        super().__init__(id=74)

    def get_damage_multiplier(self, attacker, move, effectiveness) -> float:
        if 0 < effectiveness < 1:
            return TINTED_LENS_MULTIPLIER
        return 1.0

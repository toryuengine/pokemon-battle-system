from ability.base_ability import BaseAbility

THICK_FAT_MULTIPLIER = 0.5


# あついしぼう: 受けるほのお・こおり技の威力が半分
class ThickFat(BaseAbility):
    is_breakable = True

    def __init__(self):
        super().__init__(id=25)

    def get_received_power_multiplier(self, defender, move) -> float:
        if not move.is_typeless and move.type in ("ほのお", "こおり"):
            return THICK_FAT_MULTIPLIER
        return 1.0

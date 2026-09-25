from ability.base_ability import BaseAbility
from move.base_move import CATEGORY_PHYSICAL

PURE_POWER_MULTIPLIER = 2.0


# ヨガパワー: 攻撃が2倍
class PurePower(BaseAbility):
    def __init__(self):
        super().__init__(id=7)

    def get_attack_stat_multiplier(self, attacker, move) -> float:
        if move.category == CATEGORY_PHYSICAL:
            return PURE_POWER_MULTIPLIER
        return 1.0

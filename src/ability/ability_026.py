from ability.base_ability import BaseAbility
from move.base_move import CATEGORY_PHYSICAL

GUTS_MULTIPLIER = 1.5


# こんじょう: 状態異常の間、攻撃が1.5倍
class Guts(BaseAbility):
    def __init__(self):
        super().__init__(id=26)

    def get_attack_stat_multiplier(self, attacker, move) -> float:
        if move.category == CATEGORY_PHYSICAL and attacker.current_status.status_condition is not None:
            return GUTS_MULTIPLIER
        return 1.0

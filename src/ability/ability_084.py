from ability.base_ability import BaseAbility
from move.base_move import CATEGORY_PHYSICAL

MARVEL_SCALE_MULTIPLIER = 1.5


# ふしぎなうろこ: 状態異常の間、防御が1.5倍
class MarvelScale(BaseAbility):
    is_breakable = True

    def __init__(self):
        super().__init__(id=84)

    def get_defense_stat_multiplier(self, defender, move) -> float:
        if move.category == CATEGORY_PHYSICAL and defender.current_status.status_condition is not None:
            return MARVEL_SCALE_MULTIPLIER
        return 1.0

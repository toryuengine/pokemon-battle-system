from ability.base_ability import BaseAbility
from move.base_move import CATEGORY_PHYSICAL

HUSTLE_ATTACK_MULTIPLIER = 1.5
HUSTLE_ACCURACY_MULTIPLIER = 0.8


# はりきり: 攻撃が1.5倍になるが、物理技の命中率が0.8倍
class Hustle(BaseAbility):
    def __init__(self):
        super().__init__(id=87)

    def get_attack_stat_multiplier(self, attacker, move) -> float:
        if move.category == CATEGORY_PHYSICAL:
            return HUSTLE_ATTACK_MULTIPLIER
        return 1.0

    def get_accuracy_multiplier(self, attacker, move) -> float:
        if move.category == CATEGORY_PHYSICAL:
            return HUSTLE_ACCURACY_MULTIPLIER
        return 1.0

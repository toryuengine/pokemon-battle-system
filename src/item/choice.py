from item.base_item import BaseItem
from move.base_move import CATEGORY_PHYSICAL, CATEGORY_SPECIAL

CHOICE_STAT_MULTIPLIER = 1.5
CHOICE_SCARF_SPEED_MULTIPLIER = 1.5


# こだわり系の持ち物: 最初に出した技しか選べなくなる（交代すると解除される）
class ChoiceItem(BaseItem):
    locks_move = True


# こだわりハチマキ: 攻撃の実数値1.5倍
class ChoiceBand(ChoiceItem):
    def get_attack_stat_multiplier(self, attacker, move) -> float:
        return CHOICE_STAT_MULTIPLIER if move.category == CATEGORY_PHYSICAL else 1.0


# こだわりメガネ: 特攻の実数値1.5倍
class ChoiceSpecs(ChoiceItem):
    def get_attack_stat_multiplier(self, attacker, move) -> float:
        return CHOICE_STAT_MULTIPLIER if move.category == CATEGORY_SPECIAL else 1.0


# こだわりスカーフ: 素早さ1.5倍
class ChoiceScarf(ChoiceItem):
    def get_speed_multiplier(self) -> float:
        return CHOICE_SCARF_SPEED_MULTIPLIER

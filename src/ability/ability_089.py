from ability.base_ability import BaseAbility
from move.base_move import CATEGORY_PHYSICAL

# 場に出てから効果が続くターン数（場に出たターンを1ターン目として数える）
SLOW_START_TURNS = 5
SLOW_START_MULTIPLIER = 0.5


# スロースタート: 場に出てから5ターンの間、攻撃と素早さが半分になる
class SlowStart(BaseAbility):
    def __init__(self):
        super().__init__(id=89)
        # 効果が続く残りターン数。トレースでコピーされた場合も、コピーした時点から5ターン効果が出る
        self.turns_remaining = SLOW_START_TURNS

    def on_switch_in(self, battle, pokemon):
        self.turns_remaining = SLOW_START_TURNS

    def on_end_of_turn(self, battle, pokemon):
        if self.turns_remaining > 0:
            self.turns_remaining -= 1

    def get_attack_stat_multiplier(self, attacker, move) -> float:
        if self.turns_remaining > 0 and move.category == CATEGORY_PHYSICAL:
            return SLOW_START_MULTIPLIER
        return 1.0

    def get_speed_multiplier(self, battle, pokemon) -> float:
        if self.turns_remaining > 0:
            return SLOW_START_MULTIPLIER
        return 1.0

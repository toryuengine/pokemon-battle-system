from move.base_move import BaseMove

WRING_OUT_MAX_POWER = 120


# しぼりとる: 相手の残りHPが多いほど威力が高くなる。威力 = 120 × 相手の残りHP ÷ 相手の最大HP + 1（第4世代仕様、1〜121）
class WringOut(BaseMove):
    def __init__(self):
        super().__init__(id=43)
        self.effects = []

    def get_power(self, battle, attacker, defender) -> int:
        return WRING_OUT_MAX_POWER * defender.current_status.current_hp // defender.status.hp + 1

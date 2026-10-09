from move.base_move import BaseMove

CRUSH_GRIP_MAX_POWER = 120


# にぎりつぶす: 相手の残りHPが多いほど威力が高くなる。威力 = 120 × 相手の残りHP ÷ 相手の最大HP + 1（第4世代仕様、1〜121。しぼりとると同じ式）。接触技
class CrushGrip(BaseMove):
    def __init__(self):
        super().__init__(id=270)
        self.makes_contact = True
        self.effects = []

    def get_power(self, battle, attacker, defender) -> int:
        return CRUSH_GRIP_MAX_POWER * defender.current_status.current_hp // defender.status.hp + 1

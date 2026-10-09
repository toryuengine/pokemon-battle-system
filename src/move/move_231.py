from move.base_move import BaseMove

DIVE_ID = 102


# うずしお: 当たると相手を2〜5ターン締め付け、毎ターン最大HPの1/16を削る
# ダイビングで水中にいる相手にも当たり、その場合は威力が2倍になる
class Whirlpool(BaseMove):
    def __init__(self):
        super().__init__(id=231)
        self.effects = [("bind",)]
        self.hits_during_charge_move_ids = (DIVE_ID,)

    def get_power(self, battle, attacker, defender) -> int:
        charging_move = defender.current_status.charging_move
        if charging_move is not None and charging_move.id in self.hits_during_charge_move_ids:
            return self.power * 2
        return self.power

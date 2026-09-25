from move.base_move import BaseMove

DIG_ID = 135


# じしん: あなをほるで地中にいる相手にも当たり、その場合は威力が2倍になる
class Earthquake(BaseMove):
    def __init__(self):
        super().__init__(id=8)
        self.effects = []
        self.hits_during_charge_move_ids = (DIG_ID,)

    def get_power(self, battle, attacker, defender) -> int:
        charging_move = defender.current_status.charging_move
        if charging_move is not None and charging_move.id in self.hits_during_charge_move_ids:
            return self.power * 2
        return self.power

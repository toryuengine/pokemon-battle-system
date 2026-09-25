from move.base_move import BaseMove


# しっぺがえし: 相手がこのターン既に行動していれば（自分が後から行動すれば）威力が2倍になる
class Payback(BaseMove):
    def __init__(self):
        super().__init__(id=109)
        self.effects = []

    def get_power(self, battle, attacker, defender) -> int:
        if defender.current_status.has_moved_this_turn:
            return self.power * 2
        return self.power

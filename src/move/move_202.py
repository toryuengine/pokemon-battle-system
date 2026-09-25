from move.base_move import BaseMove


# しおみず: 相手の残りHPが最大HPの半分以下なら威力が2倍になる
class Brine(BaseMove):
    def __init__(self):
        super().__init__(id=202)
        self.effects = []

    def get_power(self, battle, attacker, defender) -> int:
        if defender.current_status.current_hp * 2 <= defender.status.hp:
            return self.power * 2
        return self.power

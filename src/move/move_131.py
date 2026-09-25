from move.base_move import BaseMove


# リベンジ: 優先度-4の後攻技。このターンに今の相手から攻撃を受けてダメージを負っていれば威力が2倍になる
# (みがわりが受けた攻撃ではダメージを負っていない扱い)
class Revenge(BaseMove):
    def __init__(self):
        super().__init__(id=131)
        self.effects = []
        self.priority = -4

    def get_power(self, battle, attacker, defender) -> int:
        if attacker.current_status.damaged_by_this_turn is defender:
            return self.power * 2
        return self.power

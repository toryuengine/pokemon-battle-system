from move.base_move import BaseMove


# ゆめくい: ねむっている相手にしか効かない。与えたダメージの半分を回復する
class DreamEater(BaseMove):
    def __init__(self):
        super().__init__(id=112)
        self.effects = [('drain', 0.5)]

    def try_execute(self, battle, attacker, defender) -> bool:
        return defender.current_status.status_condition == "sleep"

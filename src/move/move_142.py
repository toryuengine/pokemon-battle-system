from move.base_move import BaseMove


# はねやすめ: 最大HPの1/2を回復し、そのターンの間ひこうタイプが無くなる（HPが満タンなら失敗する）
class Roost(BaseMove):
    def __init__(self):
        super().__init__(id=142)
        self.effects = [("roost",)]

    def try_execute(self, battle, attacker, defender) -> bool:
        return attacker.current_status.current_hp < attacker.status.hp

from move.base_move import BaseMove


# つっぱり
class ArmThrust(BaseMove):
    def __init__(self):
        super().__init__(id=148)  # 複数回攻撃は未実装
        self.effects = []

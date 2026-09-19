from move.base_move import BaseMove


# にどげり
class DoubleKick(BaseMove):
    def __init__(self):
        super().__init__(id=210)  # 複数回攻撃は未実装
        self.effects = []

from move.base_move import BaseMove


# ハイドロポンプ
class HydroPump(BaseMove):
    def __init__(self):
        super().__init__(id=8)
        self.effects = []

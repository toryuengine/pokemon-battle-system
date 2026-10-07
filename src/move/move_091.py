from move.base_move import BaseMove


# ボーンラッシュ
class BoneRush(BaseMove):
    def __init__(self):
        super().__init__(id=91)
        self.effects = []
        self.min_hits = 2
        self.max_hits = 5

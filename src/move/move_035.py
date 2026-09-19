from move.base_move import BaseMove


# アクアリング
class AquaRing(BaseMove):
    def __init__(self):
        super().__init__(id=35)
        self.effects = []

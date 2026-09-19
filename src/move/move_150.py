from move.base_move import BaseMove


# クロスチョップ
class CrossChop(BaseMove):
    def __init__(self):
        super().__init__(id=150)
        self.effects = []

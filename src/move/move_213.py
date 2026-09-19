from move.base_move import BaseMove


# クロスポイズン
class CrossPoison(BaseMove):
    def __init__(self):
        super().__init__(id=213)
        self.effects = [('status', 'target', 'poison', 0.1)]

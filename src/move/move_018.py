from move.base_move import BaseMove


# オーバーヒート
class Overheat(BaseMove):
    def __init__(self):
        super().__init__(id=18)
        self.effects = [('stat', 'self', 'spatk', -2, 1.0)]

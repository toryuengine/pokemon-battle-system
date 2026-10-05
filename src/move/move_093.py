from move.base_move import BaseMove


# はっぱカッター
class RazorLeaf(BaseMove):
    def __init__(self):
        super().__init__(id=93)
        self.effects = []
        self.high_crit = True

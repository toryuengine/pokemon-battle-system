from move.base_move import BaseMove


# ゆめくい
class DreamEater(BaseMove):
    def __init__(self):
        super().__init__(id=112)
        self.effects = [('drain', 0.5)]

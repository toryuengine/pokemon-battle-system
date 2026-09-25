from move.base_move import BaseMove


# うらみ: 相手が直前に使った技のPPを4減らす
class Spite(BaseMove):
    def __init__(self):
        super().__init__(id=226)
        self.effects = [("spite",)]

from move.base_move import BaseMove


# すてみタックル: 与えたダメージの1/3の反動を受ける
class DoubleEdge(BaseMove):
    def __init__(self):
        super().__init__(id=138)
        self.makes_contact = True
        self.effects = [('recoil', 0.3333333333333333)]

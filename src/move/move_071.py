from move.base_move import BaseMove


# ウッドハンマー
class WoodHammer(BaseMove):
    def __init__(self):
        super().__init__(id=71)
        self.effects = [('recoil', 0.3333333333333333)]

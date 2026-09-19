from move.base_move import BaseMove


# ふいうち
class Feint(BaseMove):
    def __init__(self):
        super().__init__(id=144)  # 優先度（先制技）は未対応
        self.effects = []

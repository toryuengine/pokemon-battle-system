from move.base_move import BaseMove


# ピヨピヨパンチ
class ChickPunch(BaseMove):
    def __init__(self):
        super().__init__(id=192)
        self.effects = [("status", "target", "confusion", 0.2)]

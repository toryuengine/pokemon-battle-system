from move.base_move import BaseMove


# ピヨピヨパンチ
class ChickPunch(BaseMove):
    def __init__(self):
        super().__init__(id=219)
        self.makes_contact = True
        self.effects = [("status", "target", "confusion", 0.2)]

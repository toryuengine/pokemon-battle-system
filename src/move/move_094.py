from move.base_move import BaseMove


# ドレインパンチ
class DrainPunch(BaseMove):
    def __init__(self):
        super().__init__(id=94)
        self.effects = [('drain', 0.5)]

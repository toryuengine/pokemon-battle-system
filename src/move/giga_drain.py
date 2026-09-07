from move.base_move import BaseMove


# ギガドレイン
class GigaDrain(BaseMove):
    def __init__(self):
        super().__init__(id=4)
        self.drain_ratio = 0.5

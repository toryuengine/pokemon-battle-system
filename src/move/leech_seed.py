from move.base_move import BaseMove


# やどりぎのタネ
class LeechSeed(BaseMove):
    def __init__(self):
        super().__init__(id=6)
        self.drain_ratio = 1 / 8

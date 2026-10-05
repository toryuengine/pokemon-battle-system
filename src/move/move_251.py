from move.base_move import BaseMove


# ねっぷう
class HeatWave(BaseMove):
    def __init__(self):
        super().__init__(id=251)
        self.effects = [('status', 'target', 'burn', 0.1)]

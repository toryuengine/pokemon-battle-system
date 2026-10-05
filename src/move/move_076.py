from move.base_move import BaseMove


# エアカッター
class AirCutter(BaseMove):
    def __init__(self):
        super().__init__(id=76)
        self.effects = []
        self.high_crit = True

from move.base_move import BaseMove


# エアスラッシュ
class AirSlash(BaseMove):
    def __init__(self):
        super().__init__(id=15)
        self.effects = []

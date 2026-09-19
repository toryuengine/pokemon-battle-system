from move.base_move import BaseMove


# ゆきなだれ
class Avalanche(BaseMove):
    def __init__(self):
        super().__init__(id=37)
        self.effects = []

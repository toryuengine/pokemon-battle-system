from move.base_move import BaseMove


# ヘドロばくだん
class SludgeBomb(BaseMove):
    def __init__(self):
        super().__init__(id=1)
        self.poison_chance = 0.3

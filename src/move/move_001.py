from move.base_move import BaseMove


# ヘドロばくだん
class SludgeBomb(BaseMove):
    def __init__(self):
        super().__init__(id=1)
        self.effects = [('status', 'target', 'poison', 0.3)]

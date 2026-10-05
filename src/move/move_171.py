from move.base_move import BaseMove


# マグネットボム
class MagnetBomb(BaseMove):
    def __init__(self):
        super().__init__(id=171)
        self.effects = []

from move.base_move import BaseMove


# だいもんじ
class FireBlast(BaseMove):
    def __init__(self):
        super().__init__(id=222)
        self.effects = [('status', 'target', 'burn', 0.1)]

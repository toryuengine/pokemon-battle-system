from move.base_move import BaseMove


# リーフストーム
class LeafStorm(BaseMove):
    def __init__(self):
        super().__init__(id=0)
        self.effects = [('stat', 'self', 'spatk', -2, 1.0)]

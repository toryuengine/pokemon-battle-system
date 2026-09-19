from move.base_move import BaseMove


# リーフブレード
class LeafBlade(BaseMove):
    def __init__(self):
        super().__init__(id=57)
        self.effects = []

from move.base_move import BaseMove


# マジカルリーフ
class MagicalLeaf(BaseMove):
    def __init__(self):
        super().__init__(id=136)
        self.effects = []

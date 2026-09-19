from move.base_move import BaseMove


# バリアー
class Barrier(BaseMove):
    def __init__(self):
        super().__init__(id=244)
        self.effects = [('stat', 'self', 'defense', 2, 1.0)]

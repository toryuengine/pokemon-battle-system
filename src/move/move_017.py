from move.base_move import BaseMove


# こわいかお
class ScaryFace(BaseMove):
    def __init__(self):
        super().__init__(id=17)
        self.effects = [('stat', 'target', 'spd', -2, 1.0)]

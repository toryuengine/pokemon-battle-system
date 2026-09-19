from move.base_move import BaseMove


# どくどく
class Toxic(BaseMove):
    def __init__(self):
        super().__init__(id=41)
        self.effects = [('status', 'target', 'poison', 1.0)]

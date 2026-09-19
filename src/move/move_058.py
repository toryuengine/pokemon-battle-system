from move.base_move import BaseMove


# いやなおと
class Screech(BaseMove):
    def __init__(self):
        super().__init__(id=58)
        self.effects = [('stat', 'target', 'defense', -2, 1.0)]

from move.base_move import BaseMove


# いやなおと
class Screech(BaseMove):
    def __init__(self):
        super().__init__(id=25)
        self.effects = [('stat', 'target', 'defense', -2, 1.0)]

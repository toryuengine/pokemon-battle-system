from move.base_move import BaseMove


# キノコのほうし
class Spore(BaseMove):
    def __init__(self):
        super().__init__(id=128)
        self.effects = [('status', 'target', 'sleep', 1.0)]

from move.base_move import BaseMove


# あさのひざし
class MorningSun(BaseMove):
    def __init__(self):
        super().__init__(id=263)
        self.effects = [('heal', 0.5)]

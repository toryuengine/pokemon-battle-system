from move.base_move import BaseMove


# あばれる
class Thrash(BaseMove):
    def __init__(self):
        super().__init__(id=147)
        self.effects = []

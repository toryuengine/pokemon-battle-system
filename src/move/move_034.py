from move.base_move import BaseMove


# のろい
class Curse(BaseMove):
    def __init__(self):
        super().__init__(id=34)
        self.effects = [('curse',)]

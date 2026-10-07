from move.base_move import BaseMove


# のろい
class Curse(BaseMove):
    def __init__(self):
        super().__init__(id=10)
        self.effects = [('curse',)]

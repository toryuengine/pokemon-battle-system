from move.base_move import BaseMove


# いえき
class Haze(BaseMove):
    def __init__(self):
        super().__init__(id=177)
        self.effects = [('clear_stats',)]

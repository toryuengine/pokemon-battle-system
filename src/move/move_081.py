from move.base_move import BaseMove


# なみのり
class Surf(BaseMove):
    def __init__(self):
        super().__init__(id=81)
        self.effects = []

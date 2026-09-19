from move.base_move import BaseMove


# やつあたり
class Frustration(BaseMove):
    def __init__(self):
        super().__init__(id=175)
        self.effects = []

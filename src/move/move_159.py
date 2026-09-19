from move.base_move import BaseMove


# たたきつける
class Slam(BaseMove):
    def __init__(self):
        super().__init__(id=159)
        self.effects = []

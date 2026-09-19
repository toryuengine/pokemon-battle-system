from move.base_move import BaseMove


# きりさく
class Slash(BaseMove):
    def __init__(self):
        super().__init__(id=90)
        self.effects = []

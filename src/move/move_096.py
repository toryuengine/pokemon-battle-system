from move.base_move import BaseMove


# みきり
class Detect(BaseMove):
    def __init__(self):
        super().__init__(id=96)
        self.effects = [("protect",)]
        self.priority = 3

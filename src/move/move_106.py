from move.base_move import BaseMove


# からげんき
class Facade(BaseMove):
    def __init__(self):
        super().__init__(id=106)
        self.effects = []

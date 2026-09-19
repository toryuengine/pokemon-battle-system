from move.base_move import BaseMove


# きしかいせい
class Reversal(BaseMove):
    def __init__(self):
        super().__init__(id=50)
        self.effects = []

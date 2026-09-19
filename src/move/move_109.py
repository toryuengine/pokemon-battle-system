from move.base_move import BaseMove


# しっぺがえし
class Payback(BaseMove):
    def __init__(self):
        super().__init__(id=109)
        self.effects = []

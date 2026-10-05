from move.base_move import BaseMove


# つぼをつく
class Acupressure(BaseMove):
    def __init__(self):
        super().__init__(id=150)
        self.effects = [("acupressure",)]

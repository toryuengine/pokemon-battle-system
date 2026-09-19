from move.base_move import BaseMove


# きりふだ
class TrumpCard(BaseMove):
    def __init__(self):
        super().__init__(id=252)
        self.effects = []

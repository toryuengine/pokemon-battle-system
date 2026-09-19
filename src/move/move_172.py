from move.base_move import BaseMove


# がむしゃら
class Flail(BaseMove):
    def __init__(self):
        super().__init__(id=172)
        self.effects = []

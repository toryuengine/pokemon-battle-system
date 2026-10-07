from move.base_move import BaseMove


# じわれ
class Fissure(BaseMove):
    def __init__(self):
        super().__init__(id=88)
        self.effects = []
        self.is_ohko = True

from move.base_move import BaseMove


# じこさいせい
class Recover(BaseMove):
    def __init__(self):
        super().__init__(id=84)
        self.effects = [('heal', 0.5)]

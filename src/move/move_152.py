from move.base_move import BaseMove


# じゅうでん
class Charge(BaseMove):
    def __init__(self):
        super().__init__(id=152)
        self.effects = [('charge',)]

from move.base_move import BaseMove


# じゅうでん
class Charge(BaseMove):
    def __init__(self):
        super().__init__(id=235)
        self.effects = [('stat', 'self', 'spdef', 1, 1.0)]

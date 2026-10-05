from move.base_move import BaseMove


# インファイト
class CloseCombat(BaseMove):
    def __init__(self):
        super().__init__(id=35)
        self.makes_contact = True
        self.effects = [('stat_multi', 'self', [('defense', -1), ('spdef', -1)], 1.0)]

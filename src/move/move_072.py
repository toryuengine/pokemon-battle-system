from move.base_move import BaseMove


# インファイト
class CloseCombat(BaseMove):
    def __init__(self):
        super().__init__(id=72)
        self.effects = [('stat_multi', 'self', [('defense', -1), ('spdef', -1)], 1.0)]

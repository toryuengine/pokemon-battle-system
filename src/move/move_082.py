from move.base_move import BaseMove


# ふぶき
class Blizzard(BaseMove):
    def __init__(self):
        super().__init__(id=82)
        self.effects = [('status', 'target', 'freeze', 0.1)]

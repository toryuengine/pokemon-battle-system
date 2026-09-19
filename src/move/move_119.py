from move.base_move import BaseMove


# 10まんボルト
class Thunderbolt(BaseMove):
    def __init__(self):
        super().__init__(id=119)
        self.effects = [('status', 'target', 'paralysis', 0.1)]

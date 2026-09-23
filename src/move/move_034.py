from move.base_move import BaseMove


# かげぶんしん
class DoubleTeam(BaseMove):
    def __init__(self):
        super().__init__(id=34)
        self.effects = [("stat", "self", "evasion", 1, 1.0)]

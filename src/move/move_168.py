from move.base_move import BaseMove


# ねむる
class Rest(BaseMove):
    def __init__(self):
        super().__init__(id=168)
        self.effects = [('heal', 1.0), ('status', 'self', 'sleep', 1.0)]

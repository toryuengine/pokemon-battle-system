from move.base_move import BaseMove


# うたう
class Sing(BaseMove):
    def __init__(self):
        super().__init__(id=185)
        self.effects = [('status', 'target', 'sleep', 1.0)]

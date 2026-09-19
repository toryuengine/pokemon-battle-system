from move.base_move import BaseMove


# くさぶえ
class GrassWhistle(BaseMove):
    def __init__(self):
        super().__init__(id=208)
        self.effects = [('status', 'target', 'sleep', 1.0)]

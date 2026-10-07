from move.base_move import BaseMove


# さいみんじゅつ
class Hypnosis(BaseMove):
    def __init__(self):
        super().__init__(id=118)
        self.effects = [('status', 'target', 'sleep', 1.0)]

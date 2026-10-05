from move.base_move import BaseMove


# あくまのキッス
class LovelyKiss(BaseMove):
    def __init__(self):
        super().__init__(id=53)
        self.effects = [('status', 'target', 'sleep', 1.0)]

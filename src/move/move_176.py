from move.base_move import BaseMove


# つるぎのまい
class SwordsDance(BaseMove):
    def __init__(self):
        super().__init__(id=176)
        self.effects = [('stat', 'self', 'atk', 2, 1.0)]

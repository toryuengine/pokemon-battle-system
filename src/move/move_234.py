from move.base_move import BaseMove


# とおぼえ
class Howl(BaseMove):
    def __init__(self):
        super().__init__(id=234)
        self.effects = [('stat', 'self', 'atk', 1, 1.0)]

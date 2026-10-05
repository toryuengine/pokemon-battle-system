from move.base_move import BaseMove


# あまえる
class Charm(BaseMove):
    def __init__(self):
        super().__init__(id=104)
        self.effects = [('stat', 'target', 'atk', -2, 1.0)]

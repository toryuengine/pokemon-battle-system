from move.base_move import BaseMove


# かみなり
class Thunder(BaseMove):
    def __init__(self):
        super().__init__(id=124)
        self.effects = [('status', 'target', 'paralysis', 0.3)]

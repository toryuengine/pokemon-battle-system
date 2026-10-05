from move.base_move import BaseMove


# かみなり
class Thunder(BaseMove):
    def __init__(self):
        super().__init__(id=208)
        self.effects = [('status', 'target', 'paralysis', 0.3)]

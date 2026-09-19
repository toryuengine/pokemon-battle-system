from move.base_move import BaseMove


# おどろかす
class Astonish(BaseMove):
    def __init__(self):
        super().__init__(id=84)
        self.effects = [('flinch', 'target', 0.3)]

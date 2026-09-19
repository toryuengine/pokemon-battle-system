from move.base_move import BaseMove


# どくづき
class PoisonJab(BaseMove):
    def __init__(self):
        super().__init__(id=95)
        self.effects = [('status', 'target', 'poison', 0.3)]

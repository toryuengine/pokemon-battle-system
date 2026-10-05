from move.base_move import BaseMove


# たつまき
class Twister(BaseMove):
    def __init__(self):
        super().__init__(id=237)
        self.effects = [('flinch', 'target', 0.2)]

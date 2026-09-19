from move.base_move import BaseMove


# たつまき
class Twister(BaseMove):
    def __init__(self):
        super().__init__(id=260)
        self.effects = [('flinch', 'target', 0.2)]

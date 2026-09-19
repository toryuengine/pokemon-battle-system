from move.base_move import BaseMove


# しねんのずつき
class ZenHeadbutt(BaseMove):
    def __init__(self):
        super().__init__(id=38)
        self.effects = [('flinch', 'target', 0.3)]

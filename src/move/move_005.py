from move.base_move import BaseMove


# エアスラッシュ
class AirSlash(BaseMove):
    def __init__(self):
        super().__init__(id=5)
        self.effects = [('flinch', 'target', 0.3)]

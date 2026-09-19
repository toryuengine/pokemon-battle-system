from move.base_move import BaseMove


# アームハンマー
class HammerArm(BaseMove):
    def __init__(self):
        super().__init__(id=66)
        self.effects = [('stat', 'self', 'spd', -1, 1.0)]

from move.base_move import BaseMove


# シャドーボール
class ShadowBall(BaseMove):
    def __init__(self):
        super().__init__(id=99)
        self.effects = [('stat', 'target', 'spdef', -1, 0.2)]

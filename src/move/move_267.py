from move.base_move import BaseMove


# ミストボール: 50%で相手の特攻-1
class MistBall(BaseMove):
    def __init__(self):
        super().__init__(id=267)
        self.effects = [('stat', 'target', 'spatk', -1, 0.5)]

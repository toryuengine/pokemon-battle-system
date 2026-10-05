from move.base_move import BaseMove


# エナジーボール
class EnergyBall(BaseMove):
    def __init__(self):
        super().__init__(id=131)
        self.effects = [('stat', 'target', 'spdef', -1, 0.1)]

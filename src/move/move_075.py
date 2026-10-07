from move.base_move import BaseMove


# ダストシュート
class GunkShot(BaseMove):
    def __init__(self):
        super().__init__(id=75)
        self.effects = [('status', 'target', 'poison', 0.3)]

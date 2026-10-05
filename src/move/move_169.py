from move.base_move import BaseMove


# ラスターカノン
class FlashCannon(BaseMove):
    def __init__(self):
        super().__init__(id=169)
        self.effects = [('stat', 'target', 'spdef', -1, 0.1)]

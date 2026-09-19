from move.base_move import BaseMove


# ブレイククロー
class CrushClaw(BaseMove):
    def __init__(self):
        super().__init__(id=212)
        self.effects = [('stat', 'target', 'defense', -1, 0.5)]

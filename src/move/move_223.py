from move.base_move import BaseMove


# ブレイククロー
class CrushClaw(BaseMove):
    def __init__(self):
        super().__init__(id=223)
        self.makes_contact = True
        self.effects = [('stat', 'target', 'defense', -1, 0.5)]

from move.base_move import BaseMove


# メタルクロー
class MetalClaw(BaseMove):
    def __init__(self):
        super().__init__(id=76)
        self.effects = [('stat', 'self', 'atk', 1, 0.1)]

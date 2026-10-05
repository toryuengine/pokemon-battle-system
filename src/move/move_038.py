from move.base_move import BaseMove


# メタルクロー
class MetalClaw(BaseMove):
    def __init__(self):
        super().__init__(id=38)
        self.makes_contact = True
        self.effects = [('stat', 'self', 'atk', 1, 0.1)]

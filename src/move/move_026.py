from move.base_move import BaseMove


# ブレイズキック
class BlazeKick(BaseMove):
    def __init__(self):
        super().__init__(id=26)
        self.makes_contact = True
        self.effects = [('status', 'target', 'burn', 0.1)]

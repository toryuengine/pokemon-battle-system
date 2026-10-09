from move.base_move import BaseMove


# ブレイズキック: 急所に当たりやすい
class BlazeKick(BaseMove):
    def __init__(self):
        super().__init__(id=62)
        self.makes_contact = True
        self.high_crit = True
        self.effects = [('status', 'target', 'burn', 0.1)]

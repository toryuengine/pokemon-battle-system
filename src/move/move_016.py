from move.base_move import BaseMove


# ほのおのパンチ
class FirePunch(BaseMove):
    def __init__(self):
        super().__init__(id=16)
        self.makes_contact = True
        self.effects = [('status', 'target', 'burn', 0.1)]

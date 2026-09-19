from move.base_move import BaseMove


# ほのおのパンチ
class FirePunch(BaseMove):
    def __init__(self):
        super().__init__(id=46)
        self.effects = [('status', 'target', 'burn', 0.1)]

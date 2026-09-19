from move.base_move import BaseMove


# ほのおのキバ
class FireFang(BaseMove):
    def __init__(self):
        super().__init__(id=107)
        self.effects = [('status', 'target', 'burn', 0.1), ('flinch', 'target', 0.1)]

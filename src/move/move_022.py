from move.base_move import BaseMove


# フレアドライブ
class FlareBlitz(BaseMove):
    def __init__(self):
        super().__init__(id=22)
        self.effects = [('recoil', 0.3333333333333333), ('status', 'target', 'burn', 0.1)]

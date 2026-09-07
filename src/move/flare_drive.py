from move.base_move import BaseMove


# フレアドライブ
class FlareDrive(BaseMove):
    def __init__(self):
        super().__init__(id=22)
        self.recoil_ratio = 1 / 3
        self.burn_chance = 0.1

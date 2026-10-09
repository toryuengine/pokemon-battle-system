from move.base_move import BaseMove


# フレアドライブ: 与えたダメージの1/3の反動を受ける。こおり状態でも使え、使うと自分のこおりが解ける
class FlareBlitz(BaseMove):
    def __init__(self):
        super().__init__(id=22)
        self.makes_contact = True
        self.thaws_user = True
        self.effects = [('recoil', 0.3333333333333333), ('status', 'target', 'burn', 0.1)]

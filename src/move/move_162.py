from move.base_move import BaseMove


# ボルテッカー: 与えたダメージの1/3の反動を受ける。第4世代から10%の確率で相手をまひさせる追加効果が付いた
class VoltTackle(BaseMove):
    def __init__(self):
        super().__init__(id=162)
        self.makes_contact = True
        self.effects = [('recoil', 0.3333333333333333), ('status', 'target', 'paralysis', 0.1)]

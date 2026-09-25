from move.base_move import BaseMove


# みらいよち: 使ったターンを含めて3回目のターン終了時に、相手の場に出ているポケモンを攻撃する
# 第4世代ではタイプなし扱いで、タイプ相性・タイプ一致の影響を受けない
class FutureSight(BaseMove):
    def __init__(self):
        super().__init__(id=201)
        self.effects = []
        self.is_delayed_attack = True
        self.is_typeless = True

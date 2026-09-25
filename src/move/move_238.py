from move.base_move import BaseMove


# パワートリック: 自分の攻撃と防御の実数値を入れ替える（もう一度使うと元に戻る）
class PowerTrick(BaseMove):
    def __init__(self):
        super().__init__(id=238)
        self.effects = [("power_trick",)]

from move.base_move import BaseMove


# みがわり: 最大HPの1/4を払って身代わりを作る。身代わりが残っている間、相手の攻撃は身代わりが受け、
# 相手からの状態異常・能力ランクダウン・ひるみ等の効果を防ぐ
class Substitute(BaseMove):
    def __init__(self):
        super().__init__(id=42)
        self.effects = [("substitute",)]

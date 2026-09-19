from move.base_move import BaseMove


# ハサミギロチン
class Guillotine(BaseMove):
    def __init__(self):
        super().__init__(id=229)  # 一撃必殺技は未実装
        self.effects = []

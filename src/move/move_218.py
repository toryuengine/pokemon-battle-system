from move.base_move import BaseMove


# バトンタッチ: 能力ランク等を引き継いで、手持ちの次の1体に交代する
class BatonPass(BaseMove):
    def __init__(self):
        super().__init__(id=218)
        self.effects = [("baton_pass",)]

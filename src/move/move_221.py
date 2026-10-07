from move.base_move import BaseMove


# ビルドアップ
class BulkUp(BaseMove):
    def __init__(self):
        super().__init__(id=221)
        self.effects = [('stat_multi', 'self', [('atk', 1), ('defense', 1)], 1.0)]

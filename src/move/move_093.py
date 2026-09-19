from move.base_move import BaseMove


# アイアンヘッド
class IronHead(BaseMove):
    def __init__(self):
        super().__init__(id=93)
        self.effects = [('flinch', 'target', 0.3)]

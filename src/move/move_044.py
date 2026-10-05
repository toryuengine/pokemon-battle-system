from move.base_move import BaseMove


# アイアンテール
class IronTail(BaseMove):
    def __init__(self):
        super().__init__(id=44)
        self.makes_contact = True
        self.effects = [('stat', 'target', 'defense', -1, 0.3)]

from move.base_move import BaseMove


# こおりのキバ
class IceFang(BaseMove):
    def __init__(self):
        super().__init__(id=53)
        self.effects = [('status', 'target', 'freeze', 0.1), ('flinch', 'target', 0.1)]

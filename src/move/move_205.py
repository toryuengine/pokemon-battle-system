from move.base_move import BaseMove


# ドラゴンダイブ
class DragonRush(BaseMove):
    def __init__(self):
        super().__init__(id=205)
        self.effects = [('flinch', 'target', 0.2)]

from move.base_move import BaseMove


# ドラゴンダイブ
class DragonRush(BaseMove):
    def __init__(self):
        super().__init__(id=205)
        self.makes_contact = True
        self.effects = [('flinch', 'target', 0.2)]

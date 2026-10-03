from move.base_move import BaseMove


# コメットパンチ
class MeteorMash(BaseMove):
    def __init__(self):
        super().__init__(id=266)
        self.makes_contact = True
        self.effects = [('stat', 'self', 'atk', 1, 0.2)]

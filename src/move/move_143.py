from move.base_move import BaseMove


# とける
class AcidArmor(BaseMove):
    def __init__(self):
        super().__init__(id=143)
        self.effects = [('stat', 'self', 'defense', 2, 1.0)]

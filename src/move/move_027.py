from move.base_move import BaseMove


# きしかいせい: じたばたと同じく、自分の残りHPが少ないほど威力が高くなる（20〜200）
class Reversal(BaseMove):
    def __init__(self):
        super().__init__(id=27)
        self.makes_contact = True
        self.effects = []
        self.has_hp_based_power = True

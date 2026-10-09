from move.base_move import BaseMove


# じたばた: 自分の残りHPが少ないほど威力が高くなる
class Flail(BaseMove):
    def __init__(self):
        super().__init__(id=228)
        self.makes_contact = True
        self.effects = []
        self.has_hp_based_power = True

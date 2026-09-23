from move.base_move import BaseMove


# じたばた
class Flail2(BaseMove):
    def __init__(self):
        super().__init__(id=228)
        self.effects = []
        self.has_hp_based_power = True

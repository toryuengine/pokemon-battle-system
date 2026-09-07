from move.base_move import BaseMove


# じしん
class Earthquake(BaseMove):
    def __init__(self):
        super().__init__(id=8)
        self.dig_damage_multiplier = 2

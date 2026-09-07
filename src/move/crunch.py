from move.base_move import BaseMove


class Crunch(BaseMove):
    def __init__(self):
        super().__init__(id=23)
        self.defense_down_chance = 0.2
        self.defense_down_stage = 1

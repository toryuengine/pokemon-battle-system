from move.base_move import BaseMove


# しんそく
class ExtremeSpeed(BaseMove):
    def __init__(self):
        super().__init__(id=187)
        self.makes_contact = True
        self.effects = []
        self.priority = 2

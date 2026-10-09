from move.base_move import BaseMove


# だましうち: 必ず命中する（hitrate=0）。優先度は0
class FeintAttack(BaseMove):
    def __init__(self):
        super().__init__(id=184)
        self.makes_contact = True
        self.effects = []

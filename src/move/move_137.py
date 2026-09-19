from move.base_move import BaseMove


# だいばくはつ
class Explosion(BaseMove):
    def __init__(self):
        super().__init__(id=137)
        self.effects = []

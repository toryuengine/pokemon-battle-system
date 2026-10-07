from move.base_move import BaseMove


# ぜったいれいど
class SheerCold(BaseMove):
    def __init__(self):
        super().__init__(id=166)
        self.effects = []
        self.is_ohko = True

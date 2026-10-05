from move.base_move import BaseMove


# ぜったいれいど
class SheerCold(BaseMove):
    def __init__(self):
        super().__init__(id=221)
        self.effects = []
        self.is_ohko = True

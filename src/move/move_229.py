from move.base_move import BaseMove


# ハサミギロチン
class Guillotine(BaseMove):
    def __init__(self):
        super().__init__(id=229)
        self.effects = []
        self.is_ohko = True

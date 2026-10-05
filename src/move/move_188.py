from move.base_move import BaseMove


# やどりぎのタネ
class LeechSeed(BaseMove):
    def __init__(self):
        super().__init__(id=188)
        self.effects = [("leech_seed",)]

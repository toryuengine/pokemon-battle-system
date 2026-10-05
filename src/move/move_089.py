from move.base_move import BaseMove


# いえき
class GastroAcid(BaseMove):
    def __init__(self):
        super().__init__(id=89)
        self.effects = [('suppress_ability',)]

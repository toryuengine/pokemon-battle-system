from move.base_move import BaseMove


# しんくうは
class VacuumWave(BaseMove):
    def __init__(self):
        super().__init__(id=139)
        self.effects = []
        self.priority = 1

from move.base_move import BaseMove


# しんくうは
class VacuumWave(BaseMove):
    def __init__(self):
        super().__init__(id=220)  # 優先度（先制技）は未対応
        self.effects = []

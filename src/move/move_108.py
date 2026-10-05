from move.base_move import BaseMove


# サイコカッター
class PsychoCut(BaseMove):
    def __init__(self):
        super().__init__(id=108)
        self.effects = []
        self.high_crit = True

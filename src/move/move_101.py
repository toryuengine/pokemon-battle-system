from move.base_move import BaseMove


# サイコカッター
class PsychoCut(BaseMove):
    def __init__(self):
        super().__init__(id=101)
        self.effects = []

from move.base_move import BaseMove


# いたみわけ
class PainSplit(BaseMove):
    def __init__(self):
        super().__init__(id=236)
        self.effects = [("pain_split",)]

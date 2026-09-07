from move.base_move import BaseMove


# ドわすれ
class Amnesia(BaseMove):
    def __init__(self):
        super().__init__(id=2)
        self.spdef_up_stage = 2

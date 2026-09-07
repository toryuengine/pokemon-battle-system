from move.base_move import BaseMove


# ねむりごな
class SleepPowder(BaseMove):
    def __init__(self):
        super().__init__(id=3)
        self.causes_sleep = True

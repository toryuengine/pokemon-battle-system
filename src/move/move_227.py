from move.base_move import BaseMove


# はらだいこ
class BellyDrum(BaseMove):
    def __init__(self):
        super().__init__(id=227)
        self.effects = [('belly_drum',)]

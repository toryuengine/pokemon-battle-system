from move.base_move import BaseMove


# リーフストーム
class LeafStorm(BaseMove):
    def __init__(self):
        super().__init__(id=0)
        self.spatk_drop_stage = 2

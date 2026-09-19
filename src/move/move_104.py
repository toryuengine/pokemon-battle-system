from move.base_move import BaseMove


# おんがえし
class Return(BaseMove):
    def __init__(self):
        super().__init__(id=104)
        self.effects = []

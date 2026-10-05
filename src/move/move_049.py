from move.base_move import BaseMove


# おんがえし
class Return(BaseMove):
    def __init__(self):
        super().__init__(id=49)
        self.makes_contact = True
        self.effects = []

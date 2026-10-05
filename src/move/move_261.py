from move.base_move import BaseMove


# パワーウィップ
class PowerWhip(BaseMove):
    def __init__(self):
        super().__init__(id=261)
        self.makes_contact = True
        self.effects = []

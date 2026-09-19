from move.base_move import BaseMove


# れいとうビーム
class IceBeam(BaseMove):
    def __init__(self):
        super().__init__(id=40)
        self.effects = [('status', 'target', 'freeze', 0.1)]

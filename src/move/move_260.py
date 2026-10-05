from move.base_move import BaseMove


# のしかかり
class BodySlam(BaseMove):
    def __init__(self):
        super().__init__(id=260)
        self.makes_contact = True
        self.effects = [('status', 'target', 'paralysis', 0.3)]

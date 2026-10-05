from move.base_move import BaseMove


# かみなりパンチ
class ThunderPunch(BaseMove):
    def __init__(self):
        super().__init__(id=17)
        self.makes_contact = True
        self.effects = [('status', 'target', 'paralysis', 0.1)]

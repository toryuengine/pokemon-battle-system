from move.base_move import BaseMove


# れいとうパンチ
class IcePunch(BaseMove):
    def __init__(self):
        super().__init__(id=31)
        self.makes_contact = True
        self.effects = [('status', 'target', 'freeze', 0.1)]

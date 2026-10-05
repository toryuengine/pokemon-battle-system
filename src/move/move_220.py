from move.base_move import BaseMove


# ばくれつパンチ
class DynamicPunch(BaseMove):
    def __init__(self):
        super().__init__(id=220)
        self.makes_contact = True
        self.effects = [('status', 'target', 'confusion', 1.0)]

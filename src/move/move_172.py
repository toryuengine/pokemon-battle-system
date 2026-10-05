from move.base_move import BaseMove


# シャドーパンチ
class ShadowPunch(BaseMove):
    def __init__(self):
        super().__init__(id=172)
        self.makes_contact = True
        self.effects = []

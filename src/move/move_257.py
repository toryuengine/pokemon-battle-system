from move.base_move import BaseMove


# シャドーパンチ
class ShadowPunch(BaseMove):
    def __init__(self):
        super().__init__(id=257)
        self.effects = []

from move.base_move import BaseMove


# バレットパンチ
class BulletPunch(BaseMove):
    def __init__(self):
        super().__init__(id=230)
        self.effects = []
        self.priority = 1

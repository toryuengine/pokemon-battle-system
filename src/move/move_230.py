from move.base_move import BaseMove


# バレットパンチ
class BulletPunch(BaseMove):
    def __init__(self):
        super().__init__(id=230)  # 優先度（先制技）は未対応
        self.effects = []

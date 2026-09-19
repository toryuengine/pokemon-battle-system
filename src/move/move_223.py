from move.base_move import BaseMove


# かげうち
class ShadowSneak(BaseMove):
    def __init__(self):
        super().__init__(id=223)  # 優先度（先制技）は未対応
        self.effects = []

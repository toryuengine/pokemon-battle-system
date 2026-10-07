from move.base_move import BaseMove


# リサイクル: 最後に消費した持ち物を取り戻す
class Recycle(BaseMove):
    def __init__(self):
        super().__init__(id=245)
        self.effects = [("recycle",)]

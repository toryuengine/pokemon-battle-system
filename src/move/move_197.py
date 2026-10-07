from move.base_move import BaseMove


# あくむ: ねむっている相手を、ねむっている間毎ターン最大HPの1/4ずつ削る状態にする
class Nightmare(BaseMove):
    def __init__(self):
        super().__init__(id=197)
        self.effects = [("nightmare",)]

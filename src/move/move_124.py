from move.base_move import BaseMove

FLY_ID = 141
BOUNCE_ID = 273


# かみなり: そらをとぶ・とびはねるで上空にいる相手にも当たる（威力は2倍にならない）
class Thunder(BaseMove):
    def __init__(self):
        super().__init__(id=124)
        self.effects = [('status', 'target', 'paralysis', 0.3)]
        self.hits_during_charge_move_ids = (FLY_ID, BOUNCE_ID)

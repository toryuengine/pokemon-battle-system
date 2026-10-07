from move.base_move import BaseMove

FLY_ID = 141


# スカイアッパー: そらをとぶで上空にいる相手にも当たる（じしん・なみのりと違い、威力は2倍にならない）
class SkyUppercut(BaseMove):
    def __init__(self):
        super().__init__(id=126)
        self.makes_contact = True
        self.effects = []
        self.hits_during_charge_move_ids = (FLY_ID,)

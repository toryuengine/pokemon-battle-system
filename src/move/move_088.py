from move.base_move import BaseMove

DIG_ID = 135


# じわれ: 一撃必殺技。あなをほるで地中にいる相手にも当たる
class Fissure(BaseMove):
    def __init__(self):
        super().__init__(id=88)
        self.effects = []
        self.is_ohko = True
        self.hits_during_charge_move_ids = (DIG_ID,)

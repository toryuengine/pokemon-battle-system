from move.base_move import BaseMove


# はたきおとす: 当たると相手の持ち物をはたき落とす（第4世代は威力20）
class KnockOff(BaseMove):
    def __init__(self):
        super().__init__(id=78)
        self.effects = [("knock_off",)]

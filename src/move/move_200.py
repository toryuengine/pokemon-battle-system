from move.base_move import BaseMove


# おんねん: 次に自分が行動するまでに相手の攻撃で瀕死になると、その技のPPを0にする
class Grudge(BaseMove):
    def __init__(self):
        super().__init__(id=200)
        self.effects = [("grudge",)]

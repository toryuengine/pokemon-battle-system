from move.base_move import BaseMove


# ほえる: 相手を手持ちの他のポケモンに強制的に交代させる。まもる・みきりを無視する
class Roar(BaseMove):
    def __init__(self):
        super().__init__(id=140)
        self.effects = [("force_switch",)]
        self.priority = -6
        self.bypasses_protect = True

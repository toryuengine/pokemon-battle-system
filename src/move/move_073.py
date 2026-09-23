from move.base_move import BaseMove


# とんぼがえり
class UTurn(BaseMove):
    def __init__(self):
        super().__init__(id=73)
        self.effects = [("self_switch",)]

from move.base_move import BaseMove


# とんぼがえり
class UTurn(BaseMove):
    def __init__(self):
        super().__init__(id=36)
        self.makes_contact = True
        self.effects = [("self_switch",)]

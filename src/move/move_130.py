from move.base_move import BaseMove


# むしくい: 相手がきのみを持っていれば、奪って食べてその効果を自分が得る
class BugBite(BaseMove):
    def __init__(self):
        super().__init__(id=130)
        self.makes_contact = True
        self.effects = [("eat_berry",)]

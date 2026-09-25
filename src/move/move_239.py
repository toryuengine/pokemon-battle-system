from move.base_move import BaseMove


# まきつく: 当たると相手を2〜5ターン締め付け、毎ターン最大HPの1/16を削る
class Wrap(BaseMove):
    def __init__(self):
        super().__init__(id=239)
        self.effects = [("bind",)]

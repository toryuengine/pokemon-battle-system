from move.base_move import BaseMove


# マグマストーム: 当たると相手を2〜5ターン締め付け、毎ターン最大HPの1/16を削る（第4世代仕様。まきつく・うずしおと同じ扱い）
class MagmaStorm(BaseMove):
    def __init__(self):
        super().__init__(id=269)
        self.effects = [("bind",)]

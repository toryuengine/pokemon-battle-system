from move.base_move import BaseMove


# みちづれ: 次に自分が行動するまでに相手の攻撃で瀕死になると、相手も瀕死にする
class DestinyBond(BaseMove):
    def __init__(self):
        super().__init__(id=155)
        self.effects = [("destiny_bond",)]

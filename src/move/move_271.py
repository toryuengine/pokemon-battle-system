from move.base_move import BaseMove


# こうそくスピン: 当たると、自分にかかっているしめつけ系の技・やどりぎのタネと、自分の場のまきびし・どくびし・ステルスロックを取り除く
# (ゴーストタイプに当たらなかった・外れた場合は取り除けない。第4世代では素早さは上がらない)
class RapidSpin(BaseMove):
    def __init__(self):
        super().__init__(id=271)
        self.makes_contact = True
        self.effects = [("rapid_spin",)]

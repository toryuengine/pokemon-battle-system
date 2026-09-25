from move.base_move import BaseMove


# おいうち: 本来は交代しようとしている相手に、交代前に威力2倍で攻撃する技
# プレイヤーの判断による交代が無く（瀕死・とんぼがえり・バトンタッチ・ほえるによる交代のみ）、
# 第4世代ではこれらの交代に対しておいうちは発動しないため、通常の威力40の攻撃として扱う
class Pursuit(BaseMove):
    def __init__(self):
        super().__init__(id=156)
        self.effects = []

from move.base_move import BaseMove


# だいばくはつ: 使った時点で（命中・失敗に関わらず）自分は瀕死になる。第4世代仕様で相手の防御を半分にして計算する
# 場にしめりけのポケモンがいると失敗し、自分も瀕死にならない
class Explosion(BaseMove):
    def __init__(self):
        super().__init__(id=137)
        self.effects = []
        self.user_faints_on_use = True
        self.halves_target_defense = True
        self.is_explosive = True

from move.base_move import CATEGORY_PHYSICAL, BaseMove


# わるあがき（move.jsonに存在しない特殊技のため、BaseMove.__init__は使わず自前で属性を設定する）
class Struggle(BaseMove):
    def __init__(self):
        self.id = -1
        self.name = "わるあがき"
        self.type = "ノーマル"
        self.category = CATEGORY_PHYSICAL
        self.power = 50
        self.pp = 1
        self.hitrate = 100
        self.current_pp = self.pp

        # 通常のダメージ以外に、自分が最大HPの1/4だけ反動を受ける
        self.effects = [("recoil_max_hp", 0.25)]

        self.high_crit = False
        self.is_ohko = False
        self.min_hits = 1
        self.max_hits = 1

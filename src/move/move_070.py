from move.base_move import BaseMove

# 相手の体重（kg）の上限（未満）と威力の表（第4世代仕様）。上から順に見て、最初に当てはまったものを使う
GRASS_KNOT_POWER_TABLE = [
    (10, 20),
    (25, 40),
    (50, 60),
    (100, 80),
    (200, 100),
]
GRASS_KNOT_MAX_POWER = 120


# くさむすび: 相手が重いほど威力が高くなる（20〜120）
class GrassKnot(BaseMove):
    def __init__(self):
        super().__init__(id=70)
        self.makes_contact = True
        self.effects = []

    def get_power(self, battle, attacker, defender) -> int:
        for weight_limit, power in GRASS_KNOT_POWER_TABLE:
            if defender.weight < weight_limit:
                return power
        return GRASS_KNOT_MAX_POWER

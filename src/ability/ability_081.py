from ability.base_ability import BaseAbility


# てきおうりょく: タイプ一致の倍率が1.5倍から2倍になる
class Adaptability(BaseAbility):
    stab_multiplier = 2.0

    def __init__(self):
        super().__init__(id=81)

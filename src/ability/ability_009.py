from ability.shared import HealingAbsorbAbility


# ちょすい: みず技を受けると、ダメージ・効果を受けずに最大HPの1/4回復する
class WaterAbsorb(HealingAbsorbAbility):
    absorbed_type = "みず"

    def __init__(self):
        super().__init__(id=9)

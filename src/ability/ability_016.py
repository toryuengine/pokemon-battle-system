from ability.shared import HealingAbsorbAbility


# ちくでん: でんき技を受けると、ダメージ・効果を受けずに最大HPの1/4回復する
class VoltAbsorb(HealingAbsorbAbility):
    absorbed_type = "でんき"

    def __init__(self):
        super().__init__(id=16)

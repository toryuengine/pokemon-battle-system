from ability.shared import SuperEffectiveReductionAbility


# ハードロック: 効果抜群の技のダメージが0.75倍
class SolidRock(SuperEffectiveReductionAbility):
    def __init__(self):
        super().__init__(id=80)

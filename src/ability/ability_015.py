from ability.shared import SuperEffectiveReductionAbility


# フィルター: 効果抜群の技のダメージが0.75倍
class Filter(SuperEffectiveReductionAbility):
    def __init__(self):
        super().__init__(id=15)

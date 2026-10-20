from ability.shared import StatusImmunityAbility


# やるき: ねむり状態にならない（ふみんと同じ）
class VitalSpirit(StatusImmunityAbility):
    immune_condition = "sleep"

    def __init__(self):
        super().__init__(id=91)

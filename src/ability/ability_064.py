from ability.shared import StatusImmunityAbility


# みずのベール: やけど状態にならない
class WaterVeil(StatusImmunityAbility):
    immune_condition = "burn"

    def __init__(self):
        super().__init__(id=64)

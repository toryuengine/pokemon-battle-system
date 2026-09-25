from ability.shared import StatusImmunityAbility


# ふみん: ねむり状態にならない
class Insomnia(StatusImmunityAbility):
    immune_condition = "sleep"

    def __init__(self):
        super().__init__(id=44)

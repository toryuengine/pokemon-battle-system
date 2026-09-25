from ability.shared import StatusImmunityAbility


# マイペース: こんらん状態にならない
class OwnTempo(StatusImmunityAbility):
    immune_condition = "confusion"

    def __init__(self):
        super().__init__(id=45)

from ability.shared import StatusImmunityAbility


# めんえき: どく状態にならない
class Immunity(StatusImmunityAbility):
    immune_condition = "poison"

    def __init__(self):
        super().__init__(id=82)

from ability.base_ability import BaseAbility


# どんかん: メロメロ状態にならない
class Oblivious(BaseAbility):
    is_breakable = True
    prevents_infatuation = True

    def __init__(self):
        super().__init__(id=12)

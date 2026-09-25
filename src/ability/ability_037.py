from ability.base_ability import BaseAbility


# せいしんりょく: ひるまない
class InnerFocus(BaseAbility):
    is_breakable = True
    prevents_flinch = True

    def __init__(self):
        super().__init__(id=37)

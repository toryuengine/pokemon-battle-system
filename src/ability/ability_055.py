from ability.base_ability import BaseAbility


# きゅうばん: ほえるで交代させられない
class SuctionCups(BaseAbility):
    is_breakable = True
    prevents_forced_switch = True

    def __init__(self):
        super().__init__(id=55)

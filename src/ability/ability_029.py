from ability.base_ability import BaseAbility


# ねんちゃく: はたきおとす・トリックで持ち物を奪われない
class StickyHold(BaseAbility):
    is_breakable = True
    prevents_item_removal = True

    def __init__(self):
        super().__init__(id=29)

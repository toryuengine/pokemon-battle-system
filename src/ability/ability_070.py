from ability.base_ability import BaseAbility


# ヘドロえき: 吸収技で吸われると、相手は回復する代わりに同じ量のダメージを受ける
class LiquidOoze(BaseAbility):
    damages_drainer = True

    def __init__(self):
        super().__init__(id=70)

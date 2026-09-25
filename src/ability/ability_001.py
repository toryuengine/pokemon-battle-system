from ability.shared import PinchTypeBoostAbility


# もうか: 残りHPが最大HPの1/3以下で、ほのお技の威力が1.5倍
class Blaze(PinchTypeBoostAbility):
    boosted_type = "ほのお"

    def __init__(self):
        super().__init__(id=1)

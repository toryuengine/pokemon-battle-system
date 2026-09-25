from ability.shared import PinchTypeBoostAbility


# しんりょく: 残りHPが最大HPの1/3以下で、くさ技の威力が1.5倍
class Overgrow(PinchTypeBoostAbility):
    boosted_type = "くさ"

    def __init__(self):
        super().__init__(id=0)

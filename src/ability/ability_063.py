from ability.shared import PinchTypeBoostAbility


# むしのしらせ: 残りHPが最大HPの1/3以下で、むし技の威力が1.5倍
class Swarm(PinchTypeBoostAbility):
    boosted_type = "むし"

    def __init__(self):
        super().__init__(id=63)

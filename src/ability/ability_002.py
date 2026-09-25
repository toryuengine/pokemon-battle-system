from ability.shared import PinchTypeBoostAbility


# げきりゅう: 残りHPが最大HPの1/3以下で、みず技の威力が1.5倍
class Torrent(PinchTypeBoostAbility):
    boosted_type = "みず"

    def __init__(self):
        super().__init__(id=2)

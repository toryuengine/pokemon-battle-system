from ability.base_ability import BaseAbility


# てんのめぐみ: 技の追加効果の発動率が2倍
class SereneGrace(BaseAbility):
    secondary_chance_multiplier = 2

    def __init__(self):
        super().__init__(id=83)

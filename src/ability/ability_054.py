from ability.base_ability import BaseAbility

SAME_GENDER_POWER_MULTIPLIER = 1.25
OPPOSITE_GENDER_POWER_MULTIPLIER = 0.75


# とうそうしん: 同じ性別の相手への威力1.25倍、異なる性別なら0.75倍。どちらかが性別不明なら補正なし
class Rivalry(BaseAbility):
    def __init__(self):
        super().__init__(id=54)

    def get_power_multiplier(self, attacker, defender, move, power) -> float:
        if attacker.gender is None or defender.gender is None:
            return 1.0
        if attacker.gender == defender.gender:
            return SAME_GENDER_POWER_MULTIPLIER
        return OPPOSITE_GENDER_POWER_MULTIPLIER

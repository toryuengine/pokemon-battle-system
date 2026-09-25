from ability.base_ability import BaseAbility


# ノーてんき: 場にいる間、天候の効果が無くなる（天候のターン経過は続く）
class CloudNine(BaseAbility):
    negates_weather = True

    def __init__(self):
        super().__init__(id=58)

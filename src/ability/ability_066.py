from ability.base_ability import BaseAbility


# スナイパー: 急所に当たった時のダメージが1.5倍（第4世代の急所2倍と合わせて3倍）
class Sniper(BaseAbility):
    critical_multiplier_bonus = 1.5

    def __init__(self):
        super().__init__(id=66)

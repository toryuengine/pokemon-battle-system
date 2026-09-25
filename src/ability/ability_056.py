from ability.shared import CriticalHitImmunityAbility


# カブトアーマー: 急所に当たらない
class BattleArmor(CriticalHitImmunityAbility):
    def __init__(self):
        super().__init__(id=56)

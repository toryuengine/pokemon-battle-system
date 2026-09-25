from ability.shared import CriticalHitImmunityAbility


# シェルアーマー: 急所に当たらない
class ShellArmor(CriticalHitImmunityAbility):
    def __init__(self):
        super().__init__(id=79)

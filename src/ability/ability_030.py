from ability.shared import NoBattleEffectAbility


# よびみず: 第4世代では、ダブルバトルでみず技を自分に引き寄せるだけ（シングルバトルでは効果なし）
class StormDrain(NoBattleEffectAbility):
    def __init__(self):
        super().__init__(id=30)

from ability.shared import NoBattleEffectAbility


# ひらいしん: 第4世代では、ダブルバトルででんき技を自分に引き寄せるだけ（シングルバトルでは効果なし）
class LightningRod(NoBattleEffectAbility):
    def __init__(self):
        super().__init__(id=6)

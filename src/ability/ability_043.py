from ability.shared import NoBattleEffectAbility


# ものひろい: 戦闘後に道具を拾うことがある（対戦では効果なし）
class Pickup(NoBattleEffectAbility):
    def __init__(self):
        super().__init__(id=43)

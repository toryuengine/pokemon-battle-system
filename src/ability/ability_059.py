from ability.shared import NoBattleEffectAbility


# にげあし: 野生のポケモンから必ず逃げられる（対戦では効果なし）
class RunAway(NoBattleEffectAbility):
    def __init__(self):
        super().__init__(id=59)

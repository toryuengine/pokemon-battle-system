from ability.shared import NoBattleEffectAbility


# はっこう: 野生のポケモンと出会いやすくなる（対戦では効果なし）
class Illuminate(NoBattleEffectAbility):
    def __init__(self):
        super().__init__(id=17)

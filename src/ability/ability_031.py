from ability.shared import NoBattleEffectAbility


# あくしゅう: 野生のポケモンと出会いにくくなる（第4世代では対戦での効果なし）
class Stench(NoBattleEffectAbility):
    def __init__(self):
        super().__init__(id=31)

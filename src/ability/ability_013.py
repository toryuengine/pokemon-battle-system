from ability.shared import NoBattleEffectAbility


# よちむ: 場に出た時、相手の技を1つ知る（対戦結果には影響しない）
class Forewarn(NoBattleEffectAbility):
    def __init__(self):
        super().__init__(id=13)

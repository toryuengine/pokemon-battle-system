from ability.shared import NoBattleEffectAbility


# きけんよち: 場に出た時、相手が効果抜群の技・一撃必殺技を持っていれば知らせる（対戦結果には影響しない）
class Anticipation(NoBattleEffectAbility):
    def __init__(self):
        super().__init__(id=24)

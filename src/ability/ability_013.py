from ability.shared import NoBattleEffectAbility


# よちむ: 場に出た時、相手の技を1つ知る（対戦結果には影響しない）
# 場に出た時にメッセージが出るので特性は判明する。見抜いた相手の技は観測に入れていない（README「推測で決めた細かい仕様」）
class Forewarn(NoBattleEffectAbility):
    def __init__(self):
        super().__init__(id=13)

    def on_switch_in(self, battle, pokemon):
        if not battle.is_fainted(battle.get_opponent(pokemon)):
            battle.reveal_ability(pokemon, self)

from ability.base_ability import BaseAbility


# トレース: 場に出た時、相手と同じ特性になる（場を退くと元に戻る）
class Trace(BaseAbility):
    def __init__(self):
        super().__init__(id=71)

    def on_switch_in(self, battle, pokemon):
        # abilityfactoryがこのクラスをimportしているため、循環importを避けてここで読み込む
        from ability.abilityfactory import create_ability

        opponent = battle.get_opponent(pokemon)
        if battle.is_fainted(opponent) or opponent.ability.id == self.id:
            return
        traced = create_ability(opponent.ability.id)
        pokemon.current_status.ability_before_trace = self
        pokemon.ability = traced
        traced.on_switch_in(battle, pokemon)

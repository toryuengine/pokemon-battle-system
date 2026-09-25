from ability.base_ability import BaseAbility


# うるおいボディ: あめの間、ターン終了時に状態異常が治る
class Hydration(BaseAbility):
    def __init__(self):
        super().__init__(id=28)

    def on_end_of_turn(self, battle, pokemon):
        if battle.get_effective_weather() == "rain" and pokemon.current_status.status_condition is not None:
            battle.cure_status(pokemon)

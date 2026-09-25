from ability.base_ability import BaseAbility


# いかく: 場に出た時、相手の攻撃を1段階下げる
class Intimidate(BaseAbility):
    def __init__(self):
        super().__init__(id=10)

    def on_switch_in(self, battle, pokemon):
        opponent = battle.get_opponent(pokemon)
        if battle.is_fainted(opponent):
            return
        battle.try_apply_stat_change(opponent, "atk", -1, 1.0, source=pokemon)

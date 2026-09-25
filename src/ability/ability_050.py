from ability.base_ability import BaseAbility


# しぜんかいふく: 交代で場を退くと状態異常が治る
class NaturalCure(BaseAbility):
    def __init__(self):
        super().__init__(id=50)

    def on_switch_out(self, battle, pokemon):
        battle.cure_status(pokemon)

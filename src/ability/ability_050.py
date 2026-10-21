from ability.base_ability import BaseAbility


# しぜんかいふく: 交代で場を退くと状態異常が治る
class NaturalCure(BaseAbility):
    def __init__(self):
        super().__init__(id=50)

    def on_switch_out(self, battle, pokemon):
        # 状態異常が治ったことは手持ちの表示で見えるので、治ったときは判明する扱いにする
        if pokemon.current_status.status_condition is not None:
            battle.reveal_ability(pokemon, self)
        battle.cure_status(pokemon)

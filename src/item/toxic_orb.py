from item.base_item import BaseItem


# どくどくだま: ターンの最後に、状態異常が無ければどく状態になる
# 本来は「もうどく」（悪化していくどく）になるが、どくびしと同様に簡略化して通常のどく扱いにしている
class ToxicOrb(BaseItem):
    def on_end_of_turn_late(self, battle, pokemon):
        # めんえき等の特性でどくにならないポケモンには効果がない
        if pokemon.current_status.status_condition is None and battle.can_receive_status(pokemon, "poison"):
            pokemon.current_status.status_condition = "poison"

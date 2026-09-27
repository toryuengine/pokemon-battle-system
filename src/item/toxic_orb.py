from item.base_item import BaseItem


# どくどくだま: ターンの最後に、状態異常が無ければもうどく状態になる
class ToxicOrb(BaseItem):
    def on_end_of_turn_late(self, battle, pokemon):
        # めんえき等の特性でどくにならないポケモンには効果がない
        if pokemon.current_status.status_condition is None and battle.can_receive_status(pokemon, "poison"):
            battle.inflict_poison(pokemon, badly=True)

    # なげつけるで投げつけられた相手をもうどく状態にする
    def on_flung(self, battle, target, source):
        battle.try_apply_status(target, "toxic", 1.0, source=source)

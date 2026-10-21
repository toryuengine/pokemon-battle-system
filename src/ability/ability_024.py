from ability.shared import NoBattleEffectAbility
from battlelogic.type_chart import get_move_effectiveness
from move.base_move import CATEGORY_STATUS


# きけんよち: 場に出た時、相手が効果抜群の技・一撃必殺技・だいばくはつ等を持っていれば知らせる（対戦結果には影響しない）
# 知らせた（身震いした）ときだけ特性が判明する
class Anticipation(NoBattleEffectAbility):
    def __init__(self):
        super().__init__(id=24)

    def on_switch_in(self, battle, pokemon):
        opponent = battle.get_opponent(pokemon)
        if battle.is_fainted(opponent):
            return
        if any(self._is_threat(move, pokemon) for move in opponent.moves):
            battle.reveal_ability(pokemon, self)

    @staticmethod
    def _is_threat(move, pokemon) -> bool:
        if move.is_ohko or move.is_explosive:
            return True
        if move.category == CATEGORY_STATUS or move.is_typeless:
            return False
        return get_move_effectiveness(move, pokemon) > 1

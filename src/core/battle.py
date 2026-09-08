from core.accuracy import check_hit
from core.damage import calculate_damage
from core.type_chart import get_effectiveness
from move.base_move import BaseMove
from pokemon import Pokemon


class Battle:
    def __init__(self, pokemon1: Pokemon, pokemon2: Pokemon):
        self.pokemon1 = pokemon1
        self.pokemon2 = pokemon2
        self.current_hp1 = pokemon1.status.hp
        self.current_hp2 = pokemon2.status.hp

    # targetがpokemon1/pokemon2のどちらかを見て、対応する残りHPを返す
    def get_current_hp(self, target: Pokemon) -> int:
        if target is self.pokemon1:
            return self.current_hp1
        if target is self.pokemon2:
            return self.current_hp2
        raise ValueError("target is not part of this battle")

    # targetの残りHPからdamage分を引く（0未満にはならない）
    def apply_damage(self, target: Pokemon, damage: int):
        if target is self.pokemon1:
            self.current_hp1 = max(0, self.current_hp1 - damage)
        elif target is self.pokemon2:
            self.current_hp2 = max(0, self.current_hp2 - damage)
        else:
            raise ValueError("target is not part of this battle")

    # 残りHPが0以下なら瀕死
    def is_fainted(self, target: Pokemon) -> bool:
        return self.get_current_hp(target) <= 0

    # attackerがdefenderにmoveを撃つ。命中判定→(変化技でなければ)ダメージ計算・適用の順で行い、結果を返す
    def use_move(self, attacker: Pokemon, defender: Pokemon, move: BaseMove) -> dict:
        result = {"hit": False, "damage": 0, "effectiveness": 1.0}

        if not check_hit(move.hitrate):
            return result

        result["hit"] = True

        if move.category != "変化":
            damage = calculate_damage(attacker, defender, move)
            self.apply_damage(defender, damage)
            result["damage"] = damage
            result["effectiveness"] = get_effectiveness(move.type, defender.type1, defender.type2)

        return result

    # どちらかが瀕死なら生き残っている方を返す。両方生存/両方瀕死ならNone
    def get_winner(self):
        pokemon1_fainted = self.is_fainted(self.pokemon1)
        pokemon2_fainted = self.is_fainted(self.pokemon2)

        if pokemon1_fainted and pokemon2_fainted:
            return None
        if pokemon1_fainted:
            return self.pokemon2
        if pokemon2_fainted:
            return self.pokemon1
        return None

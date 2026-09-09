import random

from battlelogic.accuracy import check_hit
from battlelogic.damage import calculate_damage
from battlelogic.stat_stage import StatStages
from battlelogic.type_chart import get_effectiveness
from move.base_move import BaseMove
from pokemon import Pokemon


class Battle:
    # 現在HPはBattleではなくPokemon側(current_status.current_hp)で管理する
    # (交代しても引き継がれる状態のため)
    def __init__(self, pokemon1: Pokemon, pokemon2: Pokemon):
        self.pokemon1 = pokemon1
        self.pokemon2 = pokemon2

        self.stages1 = StatStages()
        self.stages2 = StatStages()

    #バトルスタート
    def start_battle(self):
        while True:
            move1 = self.select_move(self.pokemon1)
            move2 = self.select_move(self.pokemon2)
            attacker, defender = self.get_attacker_and_defender(move1, move2)  # 先行後攻を取得
            attacker_move = move1 if attacker is self.pokemon1 else move2
            defender_move = move2 if attacker is self.pokemon1 else move1

            self.use_move(attacker, defender, attacker_move)
            if self.get_winner() is not None:
                break

            self.use_move(defender, attacker, defender_move)
            if self.get_winner() is not None:
                break

    # ここ
    # attackerが持つ技リストからランダムに1つ選ぶ
    def select_move(self, attacker: Pokemon) -> BaseMove:
        return random.choice(attacker.moves)

    # 素早さを比較して先攻・後攻を決める（同速なら五分五分でランダム）
    def get_attacker_and_defender(self, move1: BaseMove, move2: BaseMove):
        if self.pokemon1.status.spd > self.pokemon2.status.spd:
            return self.pokemon1, self.pokemon2
        if self.pokemon2.status.spd > self.pokemon1.status.spd:
            return self.pokemon2, self.pokemon1
        return random.sample([self.pokemon1, self.pokemon2], 2)

    # targetがpokemon1/pokemon2のどちらかを見て、対応する残りHPを返す
    def get_current_hp(self, target: Pokemon) -> int:
        if target is not self.pokemon1 and target is not self.pokemon2:
            raise ValueError("target is not part of this battle")
        return target.current_status.current_hp

    # targetの残りHPからdamage分を引く（0未満にはならない）
    def apply_damage(self, target: Pokemon, damage: int):
        if target is not self.pokemon1 and target is not self.pokemon2:
            raise ValueError("target is not part of this battle")
        target.current_status.current_hp = max(0, target.current_status.current_hp - damage)

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

        # 命中していれば、かみくだくの防御ダウンのような技固有の追加効果を発動させる（無い技はBaseMoveのデフォルトで何もしない）
        move.apply_effect(self, attacker, defender)

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

    # targetがpokemon1/pokemon2のどちらかを見て、対応するランク補正(StatStages)を返す
    def get_stages(self, target: Pokemon) -> StatStages:
        if target is self.pokemon1:
            return self.stages1
        elif target is self.pokemon2:
            return self.stages2
        else:
            raise ValueError("target is not part of this battle")

    # targetのstatランクをchangeだけ変更する（-6〜6にクランプ）
    def change_stage(self, target: Pokemon, stat: str, change: int):
        stages = self.get_stages(target)
        current_stage = getattr(stages, stat)
        new_stage = max(-6, min(6, current_stage + change))
        setattr(stages, stat, new_stage)

    # chanceの確率でstat_nameのランクをstage_amountだけ変える（かみくだくの防御ダウンなどで使う）
    def try_apply_stat_change(self, target, stat_name, stage_amount, chance):
        if random.random() < chance:
            self.change_stage(target, stat_name, stage_amount)
            return True
        return False

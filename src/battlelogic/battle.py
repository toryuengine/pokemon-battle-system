import random

from battlelogic.accuracy import check_hit
from battlelogic.damage import calculate_damage
from battlelogic.stat_stage import StatStages
from battlelogic.type_chart import get_move_effectiveness
from move.base_move import CATEGORY_STATUS, BaseMove
from move.struggle import Struggle
from pokemon import Pokemon

# 状態異常の効果値（第4世代仕様）
POISON_DAMAGE_RATIO = 1 / 8
BURN_DAMAGE_RATIO = 1 / 16
PARALYSIS_FULL_PARA_CHANCE = 0.25
FREEZE_THAW_CHANCE = 0.2
CONFUSION_SELF_HIT_CHANCE = 1 / 3
CONFUSION_SELF_HIT_RATIO = 1 / 8


class Battle:
    # 現在HPはBattleではなくPokemon側(current_status.current_hp)で管理する
    # (交代しても引き継がれる状態のため)
    def __init__(self, pokemon1: Pokemon, pokemon2: Pokemon):
        self.pokemon1 = pokemon1
        self.pokemon2 = pokemon2

        self.stages1 = StatStages()
        self.stages2 = StatStages()

    # 双方が回復技しか選ばない等でHPが減らないケースがあるため、無限ループ防止に上限を設ける
    MAX_TURNS = 1000

    #バトルスタート
    def start_battle(self):
        for _ in range(self.MAX_TURNS):
            move1 = self.select_move(self.pokemon1) #技のインスタンスが入っている
            move2 = self.select_move(self.pokemon2) #技のインスタンスが入っている
            attacker, defender = self.get_attacker_and_defender(move1, move2)  # 優先度→素早さで先行後攻を取得
            attacker_move = move1 if attacker is self.pokemon1 else move2
            defender_move = move2 if attacker is self.pokemon1 else move1

            # can_actが反動硬直・ひるみ・状態異常（ねむり/こおり/まひ/こんらん）による行動不能を
            # まとめて判定する。行動不能ならその技は不発のまま次に進む
            if self.can_act(attacker):
                self.use_move(attacker, defender, attacker_move)
                if self.get_winner() is not None:
                    break

            if self.can_act(defender):
                self.use_move(defender, attacker, defender_move)
                if self.get_winner() is not None:
                    break

            # 毎ターン終了時のどく・やけどダメージ
            self.apply_end_of_turn_status_damage()
            if self.get_winner() is not None:
                break

    # pokemonが今ターン行動できるかどうかを判定する。判定と同時に必要な状態更新も行う
    # (反動硬直・ひるみの解除、ねむり/こおりの残りターン処理、まひの判定、こんらんの自傷など)
    def can_act(self, pokemon: Pokemon) -> bool:
        status = pokemon.current_status

        # 反動硬直中（はかいこうせん等を使った直後）は必ず行動不能。このターン限りなので解除する
        if status.must_recharge:
            status.must_recharge = False
            return False

        # ひるみは1ターンだけの行動不能。判定と同時に解除する
        if status.is_flinched:
            status.is_flinched = False
            return False

        condition = status.status_condition

        if condition == "sleep":
            if status.sleep_turns_remaining <= 0:
                status.status_condition = None
            else:
                status.sleep_turns_remaining -= 1
                return False

        if condition == "freeze":
            if random.random() < FREEZE_THAW_CHANCE:
                status.status_condition = None
            else:
                return False

        if condition == "paralysis" and random.random() < PARALYSIS_FULL_PARA_CHANCE:
            return False

        if condition == "confusion":
            status.confusion_turns_remaining -= 1
            if status.confusion_turns_remaining <= 0:
                status.status_condition = None
            if random.random() < CONFUSION_SELF_HIT_CHANCE:
                damage = max(1, int(pokemon.status.hp * CONFUSION_SELF_HIT_RATIO))
                self.apply_damage(pokemon, damage)
                return False

        return True

    # 両者が瀕死でなければ、どく・やけどの残りHPダメージをこのターンの終わりに適用する
    def apply_end_of_turn_status_damage(self):
        for pokemon in (self.pokemon1, self.pokemon2):
            if self.is_fainted(pokemon):
                continue
            condition = pokemon.current_status.status_condition
            if condition == "poison":
                damage = max(1, int(pokemon.status.hp * POISON_DAMAGE_RATIO))
                self.apply_damage(pokemon, damage)
            elif condition == "burn":
                damage = max(1, int(pokemon.status.hp * BURN_DAMAGE_RATIO))
                self.apply_damage(pokemon, damage)

    # ここ
    # attackerが持つ技のうちPPが残っているものからランダムに1つ選ぶ。全て0ならわるあがきを選ぶ
    # 溜め中（ソーラービーム等の1ターン目を終えた状態）なら、選択せず溜めていた技を強制的に返す
    def select_move(self, attacker: Pokemon) -> BaseMove:
        if attacker.current_status.charging_move is not None:
            return attacker.current_status.charging_move

        usable_moves = []
        for move in attacker.moves:
            if move.current_pp > 0:
                usable_moves.append(move)

        if not usable_moves:
            return Struggle()
        return random.choice(usable_moves)

    # まず技の優先度を比較し、同じ優先度なら素早さを比較して先攻・後攻を決める（同速なら五分五分でランダム）
    def get_attacker_and_defender(self, move1: BaseMove, move2: BaseMove):
        if move1.priority != move2.priority:
            if move1.priority > move2.priority:
                return self.pokemon1, self.pokemon2
            return self.pokemon2, self.pokemon1

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

    # move.min_hits/max_hitsから今回のヒット回数を決める
    # 2〜5回攻撃(ボーンラッシュ等)は3/8, 3/8, 1/8, 1/8という第4世代仕様の確率分布、それ以外(固定回数)はそのまま使う
    def roll_hit_count(self, move: BaseMove) -> int:
        if move.min_hits == 2 and move.max_hits == 5:
            return random.choices([2, 3, 4, 5], weights=[3, 3, 1, 1])[0]
        return random.randint(move.min_hits, move.max_hits)

    # attackerがdefenderにmoveを撃つ。命中判定→(変化技でなければ)ダメージ計算・適用の順で行い、結果を返す
    # 複数回攻撃技は命中判定を1回だけ行い、そのあと決めたヒット回数分ダメージを繰り返し与える（相手が瀕死になったら打ち切り）
    def use_move(self, attacker: Pokemon, defender: Pokemon, move: BaseMove) -> dict:
        result = {"hit": False, "damage": 0, "effectiveness": 1.0, "hit_count": 0, "charging": False}

        # 1ターン目（溜め開始）かどうか。charging_moveが同じ技を指していれば、今回は2ターン目(攻撃)
        is_releasing_charge = attacker.current_status.charging_move is move

        if move.requires_charge_turn and not is_releasing_charge:
            # 溜めターン: PPだけ消費し、攻撃せずに次のターンに備える（あなをほる等は回避状態にもなる）
            move.current_pp = max(0, move.current_pp - 1)
            attacker.current_status.charging_move = move
            if move.charge_is_invulnerable:
                attacker.current_status.is_invulnerable = True
            result["charging"] = True
            return result

        if is_releasing_charge:
            # 2ターン目: 溜め状態・回避状態を解除して攻撃に移る（PPは1ターン目で消費済みなのでここでは減らさない）
            attacker.current_status.charging_move = None
            attacker.current_status.is_invulnerable = False
        else:
            # PPは命中/失敗に関わらず、使った時点で1消費する
            move.current_pp = max(0, move.current_pp - 1)

        # はかいこうせん等は命中・失敗に関わらず、使った時点で次ターンの反動硬直が確定する
        if move.requires_recharge:
            attacker.current_status.must_recharge = True

        # 相手が回避状態（あなをほる等で溜め中）なら、命中率に関わらず必ず外れる
        if defender.current_status.is_invulnerable:
            return result

        if not check_hit(move.hitrate):
            return result

        result["hit"] = True
        total_damage = 0

        # 変化技(CATEGORY_STATUS)はダメージを与えないので、物理・特殊技の時だけダメージ計算する
        if move.category != CATEGORY_STATUS:
            hit_count = self.roll_hit_count(move)
            for _ in range(hit_count):
                if self.is_fainted(defender):
                    break
                damage = calculate_damage(attacker, defender, move)
                self.apply_damage(defender, damage)
                total_damage += damage
                result["hit_count"] += 1

            result["damage"] = total_damage
            result["effectiveness"] = get_move_effectiveness(move, defender)

        # 命中していれば、技固有の追加効果を発動させる（無い技はBaseMoveのデフォルトで何もしない）
        move.apply_effect(self, attacker, defender, total_damage)

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

    # 両者の能力ランクを全て0にリセットする（はきなど）
    def reset_all_stages(self):
        self.stages1 = StatStages()
        self.stages2 = StatStages()

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

    # chanceの確率で複数の能力ランクを同時に変える（げんしのちからのような複合効果用。1回の判定で全部まとめて適用する）
    def try_apply_stat_multi_change(self, target, stat_changes, chance):
        if random.random() < chance:
            for stat_name, stage_amount in stat_changes:
                self.change_stage(target, stat_name, stage_amount)
            return True
        return False

    # chanceの確率でtargetに状態異常を付与する（既に何か状態異常が付いている場合は上書きしない）
    # ねむり・こんらんは残りターン数もあわせて設定する
    def try_apply_status(self, target, condition, chance):
        if target.current_status.status_condition is not None:
            return False
        if random.random() < chance:
            target.current_status.status_condition = condition
            if condition == "sleep":
                target.current_status.sleep_turns_remaining = random.randint(1, 3)
            elif condition == "confusion":
                target.current_status.confusion_turns_remaining = random.randint(1, 4)
            return True
        return False

    # chanceの確率でtargetをひるませる（そのターンだけ行動不能。start_battle側で判定・解除する）
    def try_apply_flinch(self, target, chance):
        if random.random() < chance:
            target.current_status.is_flinched = True
            return True
        return False

    # attacker自身がdamageのratio分だけ反動ダメージを受ける（フレアドライブなど）
    def apply_recoil(self, attacker, damage, ratio):
        recoil_damage = max(1, int(damage * ratio))
        self.apply_damage(attacker, recoil_damage)

    # attacker自身が最大HPのratio分だけ反動ダメージを受ける（わるあがきなど、与ダメージに依存しない反動）
    def apply_max_hp_recoil(self, attacker, ratio):
        recoil_damage = max(1, int(attacker.status.hp * ratio))
        self.apply_damage(attacker, recoil_damage)

    # attacker自身がdamageのratio分だけHPを回復する（ギガドレインなど）
    def apply_drain(self, attacker, damage, ratio):
        heal_amount = int(damage * ratio)
        max_hp = attacker.status.hp
        attacker.current_status.current_hp = min(max_hp, attacker.current_status.current_hp + heal_amount)

    # attacker自身が最大HPのratio分だけ回復する（じこさいせいなど）
    def apply_heal(self, attacker, ratio):
        max_hp = attacker.status.hp
        heal_amount = int(max_hp * ratio)
        attacker.current_status.current_hp = min(max_hp, attacker.current_status.current_hp + heal_amount)

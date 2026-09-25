import random

from ability.abilityfactory import create_ability
from ability.base_ability import NO_ABILITY, BaseAbility
from battlelogic.accuracy import check_hit
from battlelogic.damage import calculate_confusion_damage, calculate_damage, roll_critical
from battlelogic.stat_stage import StatStages, accuracy_stage_multiplier, stage_multiplier
from battlelogic.type_chart import TYPE_ID_FLYING, TYPE_ID_GHOST, get_effectiveness, get_move_effectiveness, get_multiplier
from move.base_move import CATEGORY_PHYSICAL, CATEGORY_SPECIAL, CATEGORY_STATUS, BaseMove
from move.movefactory import create_move
from move.struggle import Struggle
from pokemon import Pokemon, PokemonStatus
from readpokemondata import load_type_data
from trainer import Trainer

# まねっこ・ものまねでコピーできない技のID（わるあがきは技一覧に存在しないため）
STRUGGLE_ID = -1
# コピーした技のPPは元の最大PPに関わらず固定でこの値になる
COPIED_MOVE_PP = 5

# 状態異常の効果値（第4世代仕様）
POISON_DAMAGE_RATIO = 1 / 8
BURN_DAMAGE_RATIO = 1 / 16
PARALYSIS_FULL_PARA_CHANCE = 0.25
FREEZE_THAW_CHANCE = 0.2
# こんらんの自傷確率（第4世代は1/2。第7世代以降の1/3とは異なる）
CONFUSION_SELF_HIT_CHANCE = 1 / 2
# まひ状態の素早さ倍率（第4世代仕様）
PARALYSIS_SPEED_MULTIPLIER = 0.25

# のろい（ゴーストタイプ使用時）の効果値
CURSE_DAMAGE_RATIO = 1 / 4
# じゅうでんの持続。使ったターンの終わりと次のターンの終わりに1ずつ減る
CHARGE_DURATION = 2
# たくわえるの上限回数
STOCKPILE_MAX = 3

# 天候ダメージ（すなあらし・あられ）の効果値と、免疫となるタイプID
WEATHER_DAMAGE_RATIO = 1 / 16
WEATHER_IMMUNE_TYPE_IDS = {
    "sandstorm": {8, 12, 16},  # じめん、いわ、はがね
    "hail": {5},  # こおり
}
WEATHER_DURATION = 5

# 天候によって必ず命中する技・命中率が変わる技（idで個別に判定する）
THUNDER_ID = 124  # かみなり
BLIZZARD_ID = 82  # ふぶき
SOLAR_BEAM_ID = 19  # ソーラービーム

# 設置技の効果値。まきびしは層数(1〜3)に応じてダメージ割合が変わる
STEALTH_ROCK_DAMAGE_RATIO = 1 / 8
SPIKES_DAMAGE_RATIOS = {1: 1 / 8, 2: 1 / 6, 3: 1 / 4}
TYPE_ID_ROCK = 12
TYPE_ID_POISON = 7

# 壁（リフレクター・ひかりのかべ）の持続ターン数
SCREEN_DURATION = 5
# かわらわりは攻撃前に相手の場の壁を破壊する
BRICK_BREAK_ID = 77

# まもる・みきり・こらえる（本編仕様で連続成功の可否を共通の1つのカウンタで管理する）
PROTECT_FAMILY_MOVE_IDS = {51, 65, 96}  # こらえる、まもる、みきり
# 連続成功するたびに次回の成功率が1/3倍になっていく（3世代以降共通の仕様）
PROTECT_STALL_SUCCESS_RATIO = 1 / 3

# しめつけ系の技（まきつく・すなじごく・うずしお）の毎ターンのダメージ（第4世代仕様）
BIND_DAMAGE_RATIO = 1 / 16
# あくむの毎ターンのダメージ
NIGHTMARE_DAMAGE_RATIO = 1 / 4
# ちょうはつ・アンコール・かなしばりの継続ターン数の範囲（第4世代仕様。使ったターンの終わりから1ずつ減る）
TAUNT_TURNS_RANGE = (3, 5)
ENCORE_TURNS_RANGE = (4, 8)
DISABLE_TURNS_RANGE = (4, 7)
# でんじふゆうの継続ターン数
MAGNET_RISE_DURATION = 5
# うらみで減らすPP（第4世代仕様）
SPITE_PP_REDUCTION = 4
# みらいよちは使ったターンを含めて3回目のターン終了時に攻撃する
FUTURE_SIGHT_DELAY = 3
# のみこむの回復量（たくわえた回数ごとの最大HPに対する割合）
SWALLOW_HEAL_RATIOS = {1: 1 / 4, 2: 1 / 2, 3: 1.0}
# アンコールで固定できない技（アンコール自身）。まねっこ・ものまね・わるあがきも固定できない
ENCORE_ID = 164
# みがわりで払うHPの、最大HPに対する割合
SUBSTITUTE_HP_RATIO = 1 / 4
# 相手に向けた効果のうち、みがわりを無視して届くもの（第4世代仕様: ほえる・ちょうはつ・アンコール・かなしばり・
# いちゃもん・うらみ・ゴーストタイプののろい）
SUBSTITUTE_BYPASS_EFFECT_KINDS = {"force_switch", "taunt", "encore", "disable", "torment", "spite", "curse"}

# ねをはる・アクアリングの毎ターンの回復量と、やどりぎのタネで毎ターン奪うHP（いずれも最大HPに対する割合）
INGRAIN_HEAL_RATIO = 1 / 16
AQUA_RING_HEAL_RATIO = 1 / 16
LEECH_SEED_DRAIN_RATIO = 1 / 8
TYPE_ID_GRASS = 4
# あくびは使ったターンと次のターンの終わりに1ずつ減り、0になった時点でねむる
YAWN_DURATION = 2
# ほろびのうたは使ったターンの終わりにカウント3になり、以降毎ターン1ずつ減ってカウント0になったターンの終わりに瀕死になる
# (使ったターンを含めて4回目のターン終了時)
PERISH_SONG_DURATION = 4
# メロメロ状態で動けなくなる確率
INFATUATION_IMMOBILIZE_CHANCE = 1 / 2
# トリックルームは使ったターンを含めて5ターン続く
TRICK_ROOM_DURATION = 5
# つぼをつくで上がるランクと、その対象になる能力
ACUPRESSURE_STAGES = 2
ACUPRESSURE_STATS = ("atk", "defense", "spatk", "spdef", "spd", "accuracy", "evasion")


class Battle:
    # 現在HPはBattleではなくPokemon側(current_status.current_hp)で管理する
    # (交代しても引き継がれる状態のため)
    # side1/side2はTrainerを渡す想定だが、単体のPokemonを渡した場合は
    # 手持ち1体だけのTrainerとして扱う（今までのBattle(pokemon1, pokemon2)呼び出しと互換）
    def __init__(self, side1, side2):
        self.trainer1: Trainer = side1 if isinstance(side1, Trainer) else Trainer([side1])
        self.trainer2: Trainer = side2 if isinstance(side2, Trainer) else Trainer([side2])

        self.stages1 = StatStages()
        self.stages2 = StatStages()

        # 天候（None/"sun"/"rain"/"sandstorm"/"hail"）と残りターン数
        self.weather = None
        self.weather_turns_remaining = 0

        # トリックルームの残りターン数（0なら無し）。0より大きい間は、同じ優先度の中で素早さの遅い順に行動する
        self.trick_room_turns_remaining = 0

        # 今処理している攻撃を、みがわりが受け止めた相手（Noneなら無し）。攻撃で身代わりが壊れた場合も、
        # その攻撃の追加効果・持ち物の効果（おうじゃのしるし等）は本体に届かないため、攻撃の処理中だけ保持する
        self.substitute_absorbed_target = None

    # 双方が回復技しか選ばない等でHPが減らないケースがあるため、無限ループ防止に上限を設ける
    MAX_TURNS = 1000

    # 場に出ている現在の1体目。手持ちが交代してもここは常に「今出ている個体」を指す
    @property
    def pokemon1(self) -> Pokemon:
        return self.trainer1.active

    # 場に出ている現在の2体目
    @property
    def pokemon2(self) -> Pokemon:
        return self.trainer2.active

    #バトルスタート
    def start_battle(self):
        # 対戦開始時に場に出ている両者の特性（いかく・すなおこし等）を発動させる
        self.activate_switch_in_abilities([self.pokemon1, self.pokemon2])
        self.activate_held_items_on_field()

        for _ in range(self.MAX_TURNS):
            # まもる・みきり・こらえる・ひるみの効果は使ったそのターン限りなので、新しいターンの頭でリセットする
            # (後攻の技でひるんだ先攻側が、次のターンに行動不能にならないようにするため、ひるみもここで解除する)
            for pokemon in (self.pokemon1, self.pokemon2):
                pokemon.current_status.is_protected = False
                pokemon.current_status.is_enduring = False
                pokemon.current_status.is_flinched = False
                pokemon.current_status.has_moved_this_turn = False

            move1 = self.select_move(self.pokemon1) #技のインスタンスが入っている
            move2 = self.select_move(self.pokemon2) #技のインスタンスが入っている
            first_mover, second_mover = self.get_attacker_and_defender(move1, move2)  # 優先度→素早さで先行後攻を取得
            first_move = move1 if first_mover is self.pokemon1 else move2
            second_move = move2 if first_mover is self.pokemon1 else move1
            second_trainer = self.trainer1 if second_mover is self.pokemon1 else self.trainer2

            # can_actが反動硬直・ひるみ・状態異常（ねむり/こおり/まひ/こんらん）による行動不能を
            # まとめて判定する。行動不能ならその技は不発のまま次に進む
            if self.can_act(first_mover, first_move):
                self.use_move(first_mover, second_mover, first_move)
            first_mover.current_status.has_moved_this_turn = True
            # HPが減った・状態異常になった・能力が下がった等で、きのみ・しろいハーブが発動する
            self.activate_held_items_on_field()
            # 瀕死になった側がいれば手持ちから次の1体に自動で交代させる（設置技もここで発動する）
            self.resolve_faints()
            if self.is_battle_over():
                break

            # 後攻側(second_mover)がこの攻撃で瀕死になり別の個体に交代していたら、
            # 交代してきたばかりの個体は今ターンもう行動できない
            if second_trainer.active is not second_mover:
                continue

            # 先攻側が反動等で自滅して交代していた場合に備えて、攻撃対象は今現在の相手を改めて取得する
            current_opponent = self.pokemon1 if second_mover is self.pokemon2 else self.pokemon2

            if self.can_act(second_mover, second_move):
                self.use_move(second_mover, current_opponent, second_move)
            second_mover.current_status.has_moved_this_turn = True
            self.activate_held_items_on_field()
            self.resolve_faints()
            if self.is_battle_over():
                break

            # みらいよちの攻撃
            self.apply_future_sight()
            self.activate_held_items_on_field()
            self.resolve_faints()
            if self.is_battle_over():
                break

            # 毎ターン終了時のねをはる・アクアリングの回復、やどりぎのタネの吸収、どく・やけど・のろい・あくむ・しめつけのダメージ
            self.apply_end_of_turn_recovery()
            self.apply_end_of_turn_leech_seed()
            self.apply_end_of_turn_status_damage()
            self.activate_held_items_on_field()
            self.resolve_faints()
            if self.is_battle_over():
                break

            self.apply_end_of_turn_weather_damage()
            # あめうけざら・かそく等、ターン終了時に発動する特性
            self.apply_end_of_turn_abilities()
            # たべのこし・くろいヘドロの回復/ダメージ
            self.apply_end_of_turn_items()
            self.tick_weather()
            self.tick_screens()
            self.tick_charge()
            self.tick_trick_room()
            # ちょうはつ・アンコール・かなしばり・でんじふゆう・あくびの残りターン
            self.tick_volatile_statuses()
            # ほろびのうたのカウント
            self.apply_perish_song()
            # どくどくだまはターンの最後に発動する
            self.apply_end_of_turn_orbs()
            self.activate_held_items_on_field()
            self.resolve_faints()
            if self.is_battle_over():
                break

    # どちらかのトレーナーが全滅していれば対戦は終了（get_winner()は引き分けの場合Noneを返すため、
    # 「決着したか」の判定にはget_winner()ではなくこちらを使う）
    def is_battle_over(self) -> bool:
        return self.trainer1.is_defeated() or self.trainer2.is_defeated()

    # 場に出ているポケモンが瀕死なら、手持ちの中から生きている次の1体に自動で交代させる
    # (交代先も設置技等で瀕死になる可能性があるため、生きている個体が出るか手持ちが尽きるまで繰り返す)
    # 両者が同時に瀕死になった場合に、相手の交代先が出る前に特性（いかく等）が発動しないよう、
    # 特性は両者の交代が済んでからまとめて発動させる
    def resolve_faints(self):
        switched_trainers = []
        for trainer in (self.trainer1, self.trainer2):
            while self.is_fainted(trainer.active) and not trainer.is_defeated():
                next_index = trainer.find_next_alive_index()
                if next_index is None:
                    break
                self.switch_in(trainer, next_index, activate_ability=False)
                if trainer not in switched_trainers:
                    switched_trainers.append(trainer)

        if switched_trainers:
            self.activate_switch_in_abilities([trainer.active for trainer in switched_trainers])
            self.activate_held_items_on_field()

    # 場に出たpokemonsの特性を、素早さが高い順に発動させる（同速ならランダム）
    def activate_switch_in_abilities(self, pokemons):
        ordered = sorted(pokemons, key=lambda p: (self.get_effective_speed(p), random.random()), reverse=True)
        for pokemon in ordered:
            if pokemon is not self.pokemon1 and pokemon is not self.pokemon2:
                continue
            if self.is_fainted(pokemon):
                continue
            self.get_ability(pokemon).on_switch_in(self, pokemon)

    # trainerの場のポケモンをnew_indexの個体に交代させる。能力ランクをリセットし、設置技の効果を適用する
    # activate_ability=Falseなら、場に出た時の特性は呼び出し側でまとめて発動させる
    # baton_pass=Trueなら、能力ランク・こんらん等のバトンタッチで引き継がれる状態を交代先に引き継ぐ
    def switch_in(self, trainer: Trainer, new_index: int, activate_ability: bool = True, baton_pass: bool = False):
        outgoing = trainer.active
        outgoing_status = outgoing.current_status

        # バトンタッチで引き継ぐ状態（第4世代仕様: 能力ランク・こんらん・のろい・くろいまなざし・でんじふゆう・いえき・
        # みがわり・ねをはる・アクアリング・やどりぎのタネ・ほろびのうた）
        passed_stages = self.get_stages(outgoing) if baton_pass else None
        passed_status = {
            "confusion_turns_remaining": outgoing_status.confusion_turns_remaining,
            "is_cursed": outgoing_status.is_cursed,
            "trapped_by": outgoing_status.trapped_by,
            "magnet_rise_turns_remaining": outgoing_status.magnet_rise_turns_remaining,
            "is_ability_suppressed": outgoing_status.is_ability_suppressed,
            "substitute_hp": outgoing_status.substitute_hp,
            "is_ingrained": outgoing_status.is_ingrained,
            "has_aqua_ring": outgoing_status.has_aqua_ring,
            "is_seeded": outgoing_status.is_seeded,
            "perish_turns_remaining": outgoing_status.perish_turns_remaining,
        } if baton_pass else None
        passed_power_trick = baton_pass and outgoing_status.is_power_trick_active

        # しぜんかいふく等、場を退く時に発動する特性（瀕死で退く場合は発動しない）
        if not self.is_fainted(outgoing):
            self.get_ability(outgoing).on_switch_out(self, outgoing)
        # トレースでコピーした特性は、場を退くと元のトレースに戻る
        if outgoing_status.ability_before_trace is not None:
            outgoing.ability = outgoing_status.ability_before_trace
            outgoing_status.ability_before_trace = None

        # みやぶるの「見破られた」状態、まもる・みきり・こらえるの連続成功カウンタは、場を退くと解除される
        outgoing_status.is_identified = False
        outgoing_status.protect_stall_counter = 0
        # こんらん・じゅうでん・のろい・たくわえる・いえきの効果も、場を退くと解除される
        outgoing_status.confusion_turns_remaining = 0
        outgoing_status.charge_turns_remaining = 0
        outgoing_status.is_cursed = False
        outgoing_status.stockpile_count = 0
        outgoing_status.is_ability_suppressed = False
        # こだわり系の持ち物による技の固定と、メトロノームの連続使用回数も、場を退くと解除される
        outgoing_status.choice_locked_move = None
        outgoing_status.consecutive_move_count = 0
        # 交代・拘束・技の制限に関する状態も、場を退くと解除される
        self.clear_volatile_statuses(outgoing)
        # 退いた個体が締め付けていた・逃げられなくしていた・メロメロにしていた相手は解放される
        opponent_trainer = self.trainer2 if trainer is self.trainer1 else self.trainer1
        opponent_status = opponent_trainer.active.current_status
        if opponent_status.bound_by is outgoing:
            opponent_status.bound_turns_remaining = 0
            opponent_status.bound_by = None
        if opponent_status.trapped_by is outgoing:
            opponent_status.trapped_by = None
        if opponent_status.infatuated_by is outgoing:
            opponent_status.infatuated_by = None

        trainer.active_index = new_index
        new_stages = passed_stages if passed_stages is not None else StatStages()
        if trainer is self.trainer1:
            self.stages1 = new_stages
        else:
            self.stages2 = new_stages
        if passed_status is not None:
            for name, value in passed_status.items():
                setattr(trainer.active.current_status, name, value)
        # パワートリックをバトンタッチで引き継いだ場合は、交代先の攻撃と防御の実数値を入れ替える
        if passed_power_trick:
            self.perform_power_trick(trainer.active)
        self.apply_entry_hazards(trainer)
        if not self.is_fainted(trainer.active):
            if activate_ability:
                self.get_ability(trainer.active).on_switch_in(self, trainer.active)
            # どくびしでどくになった直後にラムのみで回復する、といった持ち物の発動
            # (いかくで下がった攻撃をしろいハーブで戻す等、特性の発動後に判定する)
            self.activate_held_items_on_field()

    # trainerが持つ罠(ステルスロック・まきびし・どくびし)を、今場に出ている個体に適用する
    def apply_entry_hazards(self, trainer: Trainer):
        pokemon = trainer.active
        if self.is_fainted(pokemon):
            return

        # ひこうタイプ・ふゆうは地面にいないので、まきびし・どくびしを受けない（くろいてっきゅうを持っていれば受ける）
        is_grounded = self.is_grounded(pokemon)

        if trainer.spikes > 0 and is_grounded:
            ratio = SPIKES_DAMAGE_RATIOS[trainer.spikes]
            damage = max(1, int(pokemon.status.hp * ratio))
            self.apply_damage(pokemon, damage)

        if trainer.stealth_rock:
            effectiveness = get_effectiveness(TYPE_ID_ROCK, pokemon.type1, pokemon.type2)
            damage = max(1, int(pokemon.status.hp * STEALTH_ROCK_DAMAGE_RATIO * effectiveness))
            self.apply_damage(pokemon, damage)

        if trainer.toxic_spikes > 0 and is_grounded:
            if TYPE_ID_POISON in (pokemon.type1, pokemon.type2):
                # どくタイプが出ると、どくびしはその場から消滅する
                trainer.toxic_spikes = 0
            elif pokemon.current_status.status_condition is None and self.can_receive_status(pokemon, "poison"):
                # 本来は2層で「もうどく」（悪化していくどく）になるが、簡略化して通常のどく扱いにしている
                pokemon.current_status.status_condition = "poison"

    # pokemonが地面にいるかどうか（まきびし・どくびしを受けるか）。くろいてっきゅうを持っている、
    # またはねをはるで根を張っていれば常に地面にいる扱い
    def is_grounded(self, pokemon: Pokemon) -> bool:
        if pokemon.is_forced_grounded:
            return True
        if pokemon.current_status.magnet_rise_turns_remaining > 0:
            return False
        if self.get_ability(pokemon).is_levitating:
            return False
        return TYPE_ID_FLYING not in (pokemon.type1, pokemon.type2)

    # pokemonの今有効な特性。いえきで消されていれば「特性なし」(NO_ABILITY)を返す
    def get_ability(self, pokemon: Pokemon) -> BaseAbility:
        if pokemon.current_status.is_ability_suppressed:
            return NO_ABILITY
        return pokemon.ability

    # sourceの技・特性の効果を受けるtargetの特性。sourceがかたやぶりなら、受ける側で働く特性(is_breakable)を無視する
    def get_target_ability(self, target: Pokemon, source: Pokemon = None) -> BaseAbility:
        ability = self.get_ability(target)
        if source is None or source is target:
            return ability
        if ability.is_breakable and self.get_ability(source).ignores_target_ability:
            return NO_ABILITY
        return ability

    # pokemonの対戦相手（場に出ている方）
    def get_opponent(self, pokemon: Pokemon) -> Pokemon:
        if pokemon is self.pokemon1:
            return self.pokemon2
        if pokemon is self.pokemon2:
            return self.pokemon1
        raise ValueError("pokemon is not part of this battle")

    # 天候の効果を判定する時に使う天候。場にノーてんきのポケモンがいれば、天候は無いものとして扱う
    # (天候そのものは消えず、ターン経過も続く)
    def get_effective_weather(self):
        for pokemon in (self.pokemon1, self.pokemon2):
            if not self.is_fainted(pokemon) and self.get_ability(pokemon).negates_weather:
                return None
        return self.weather

    # pokemonがconditionの状態異常にかかるかどうか（特性による無効化）。sourceがかたやぶりなら特性を無視する
    def can_receive_status(self, pokemon: Pokemon, condition: str, source: Pokemon = None) -> bool:
        return self.get_target_ability(pokemon, source).can_receive_status(self, pokemon, condition)

    # targetのトレーナー（罠等を管理している側）を返す
    def get_trainer(self, target: Pokemon) -> Trainer:
        if target is self.pokemon1:
            return self.trainer1
        if target is self.pokemon2:
            return self.trainer2
        raise ValueError("target is not part of this battle")

    # hazard_typeをtrainerの場に設置する（まきびしは3層、どくびしは2層まで重ねがけできる）
    def add_hazard(self, trainer: Trainer, hazard_type: str):
        if hazard_type == "stealth_rock":
            trainer.stealth_rock = True
        elif hazard_type == "spikes":
            trainer.spikes = min(3, trainer.spikes + 1)
        elif hazard_type == "toxic_spikes":
            trainer.toxic_spikes = min(2, trainer.toxic_spikes + 1)

    # 壁(リフレクター/ひかりのかべ)をtrainerの場に張る（5ターン継続。使ったポケモンがひかりのねんどを持っていれば8ターン）
    def set_screen(self, trainer: Trainer, screen_type: str, user: Pokemon = None):
        duration = SCREEN_DURATION
        if user is not None:
            duration = user.held_item.get_screen_duration(duration)

        if screen_type == "reflect":
            trainer.reflect_turns_remaining = duration
        elif screen_type == "light_screen":
            trainer.light_screen_turns_remaining = duration

    # 両トレーナーの壁の残りターンを1減らす
    def tick_screens(self):
        for trainer in (self.trainer1, self.trainer2):
            if trainer.reflect_turns_remaining > 0:
                trainer.reflect_turns_remaining -= 1
            if trainer.light_screen_turns_remaining > 0:
                trainer.light_screen_turns_remaining -= 1

    # moveのカテゴリに対応する壁が、defenderの場に張られているかどうか
    def is_screen_active(self, defender: Pokemon, move: BaseMove) -> bool:
        trainer = self.get_trainer(defender)
        if move.category == CATEGORY_PHYSICAL:
            return trainer.reflect_turns_remaining > 0
        if move.category == CATEGORY_SPECIAL:
            return trainer.light_screen_turns_remaining > 0
        return False

    # pokemonが今ターン行動できるかどうかを判定する。判定と同時に必要な状態更新も行う
    # (反動硬直・ひるみの解除、ねむり/こおりの残りターン処理、まひの判定、こんらんの自傷など)
    # moveはこのターン使おうとしている技（ねごとのように、ねむり状態でも使える技の判定に使う）
    def can_act(self, pokemon: Pokemon, move: BaseMove = None) -> bool:
        status = pokemon.current_status
        ability = self.get_ability(pokemon)

        # みちづれ・おんねんは「次に自分が行動しようとするまで」有効なので、行動しようとした時点で解除する
        status.is_destiny_bond_active = False
        status.is_grudge_active = False

        # なまけ: 行動した次のターンはなまけて行動できない（反動硬直のターンと重なった場合は硬直も解除される）
        if not ability.on_before_action(self, pokemon):
            status.must_recharge = False
            return False

        # 反動硬直中（はかいこうせん等を使った直後）は必ず行動不能。このターン限りなので解除する
        if status.must_recharge:
            status.must_recharge = False
            return False

        # ひるみは1ターンだけの行動不能。判定と同時に解除する
        if status.is_flinched:
            status.is_flinched = False
            # ふくつのこころ: ひるむと素早さが上がる
            ability.on_flinched(self, pokemon)
            return False

        condition = status.status_condition

        if condition == "sleep":
            if status.sleep_turns_remaining <= 0:
                status.status_condition = None
            else:
                # はやおきなら残りターンが2倍の速さで減る
                status.sleep_turns_remaining -= ability.sleep_turn_decrement
                # ねごとはねむったまま使える
                if move is None or not move.usable_while_asleep:
                    return False

        if condition == "freeze":
            if random.random() < FREEZE_THAW_CHANCE:
                status.status_condition = None
            else:
                return False

        # こんらんはstatus_conditionとは別枠なので、どく・まひ等と重複していても判定する
        # 残りターンが尽きていれば、このターンの行動前に解ける
        if status.confusion_turns_remaining > 0:
            status.confusion_turns_remaining -= 1
            if status.confusion_turns_remaining > 0 and random.random() < CONFUSION_SELF_HIT_CHANCE:
                self.apply_damage(pokemon, calculate_confusion_damage(pokemon, self.get_stages(pokemon)))
                return False

        # メロメロ状態なら、1/2の確率で動けない
        if status.infatuated_by is not None and random.random() < INFATUATION_IMMOBILIZE_CHANCE:
            return False

        if condition == "paralysis" and random.random() < PARALYSIS_FULL_PARA_CHANCE:
            return False

        return True

    # 両者が瀕死でなければ、どく・やけどの残りHPダメージをこのターンの終わりに適用する
    def apply_end_of_turn_status_damage(self):
        for pokemon in (self.pokemon1, self.pokemon2):
            if self.is_fainted(pokemon):
                continue
            condition = pokemon.current_status.status_condition
            # ポイズンヒール・たいねつは、どく・やけどのダメージの代わりに独自の処理をする
            if condition in ("poison", "burn") and self.get_ability(pokemon).on_residual_status(self, pokemon, condition):
                pass
            elif condition == "poison":
                damage = max(1, int(pokemon.status.hp * POISON_DAMAGE_RATIO))
                self.apply_damage(pokemon, damage)
            elif condition == "burn":
                damage = max(1, int(pokemon.status.hp * BURN_DAMAGE_RATIO))
                self.apply_damage(pokemon, damage)

            # あくむ状態なら、ねむっている間は最大HPの1/4を失う（目覚めていれば解除される）
            status = pokemon.current_status
            if status.has_nightmare and status.status_condition != "sleep":
                status.has_nightmare = False
            if status.has_nightmare and not self.is_fainted(pokemon):
                self.apply_damage(pokemon, max(1, int(pokemon.status.hp * NIGHTMARE_DAMAGE_RATIO)))

            # のろい状態なら、どく・やけどとは別に最大HPの1/4を失う
            if pokemon.current_status.is_cursed and not self.is_fainted(pokemon):
                damage = max(1, int(pokemon.status.hp * CURSE_DAMAGE_RATIO))
                self.apply_damage(pokemon, damage)

            # しめつけ系の技で締め付けられていれば、最大HPの1/16を失う
            if status.bound_turns_remaining > 0 and not self.is_fainted(pokemon):
                self.apply_damage(pokemon, max(1, int(pokemon.status.hp * BIND_DAMAGE_RATIO)))
                status.bound_turns_remaining -= 1
                if status.bound_turns_remaining <= 0:
                    status.bound_by = None

    # 天候を変える（5ターン継続）。にほんばれ・あまごい・すなあらし・あられから呼ばれる
    # 使ったポケモンが対応する岩（あついいわ・しめったいわ・つめたいいわ）を持っていれば8ターン継続する
    # permanent=True（すなおこし・ゆきふらし）なら、第4世代仕様でターン経過では終わらない（残りターンをNoneにする）
    def set_weather(self, weather, user: Pokemon = None, permanent: bool = False):
        self.weather = weather
        self.weather_turns_remaining = WEATHER_DURATION
        if permanent:
            self.weather_turns_remaining = None
        elif user is not None:
            self.weather_turns_remaining = user.held_item.get_weather_duration(weather, WEATHER_DURATION)

    # 天候の残りターンを1減らし、0になったら天候を晴天(なし)に戻す
    def tick_weather(self):
        if self.weather is None or self.weather_turns_remaining is None:
            return
        self.weather_turns_remaining -= 1
        if self.weather_turns_remaining <= 0:
            self.weather = None

    # すなあらし・あられの間、免疫タイプ・特性（すながくれ等）以外に毎ターン終了時ダメージを与える
    def apply_end_of_turn_weather_damage(self):
        weather = self.get_effective_weather()
        immune_type_ids = WEATHER_IMMUNE_TYPE_IDS.get(weather)
        if immune_type_ids is None:
            return

        for pokemon in (self.pokemon1, self.pokemon2):
            if self.is_fainted(pokemon):
                continue
            if pokemon.type1 in immune_type_ids or pokemon.type2 in immune_type_ids:
                continue
            if weather in self.get_ability(pokemon).weather_immunities:
                continue
            damage = max(1, int(pokemon.status.hp * WEATHER_DAMAGE_RATIO))
            self.apply_damage(pokemon, damage)

    # ターン終了時に発動する特性（あめうけざら・アイスボディ・かんそうはだ・うるおいボディ・かそく）
    def apply_end_of_turn_abilities(self):
        for pokemon in (self.pokemon1, self.pokemon2):
            if self.is_fainted(pokemon):
                continue
            self.get_ability(pokemon).on_end_of_turn(self, pokemon)

    # ここ
    # attackerが持つ技のうちPPが残っているものからランダムに1つ選ぶ。全て0ならわるあがきを選ぶ
    # 溜め中（ソーラービーム等の1ターン目を終えた状態）なら、選択せず溜めていた技を強制的に返す
    # かなしばり・ちょうはつ・いちゃもんで選べない技は除き、アンコール中はその技しか選べない
    def select_move(self, attacker: Pokemon) -> BaseMove:
        status = attacker.current_status
        if status.charging_move is not None:
            return status.charging_move

        # アンコールで固定されていれば、その技しか選べない（PPが尽きるか技構成から消えたらアンコールが解ける）
        encore_move = status.encore_move
        if encore_move is not None:
            if encore_move.current_pp > 0 and any(move is encore_move for move in attacker.moves):
                return encore_move
            status.encore_move = None
            status.encore_turns_remaining = 0

        # こだわり系の持ち物で技が固定されていれば、その技しか選べない（PPが尽きたらわるあがき）
        # まねっこ等で固定された技が技構成から消えていれば、固定を解除する
        locked_move = status.choice_locked_move
        if locked_move is not None:
            if any(move is locked_move for move in attacker.moves):
                if locked_move.current_pp > 0 and self.is_move_selectable(attacker, locked_move):
                    return locked_move
                return Struggle()
            status.choice_locked_move = None

        usable_moves = []
        for move in attacker.moves:
            if move.current_pp > 0 and self.is_move_selectable(attacker, move):
                usable_moves.append(move)

        if not usable_moves:
            return Struggle()
        return random.choice(usable_moves)

    # かなしばり・ちょうはつ・いちゃもんの制限を受けず、pokemonがmoveを選べるかどうか（PPの残りは見ない）
    def is_move_selectable(self, pokemon: Pokemon, move: BaseMove) -> bool:
        status = pokemon.current_status
        if status.disabled_move is move:
            return False
        if status.taunt_turns_remaining > 0 and move.category == CATEGORY_STATUS:
            return False
        if status.is_tormented and move.id == status.last_move_used_id:
            return False
        return True

    # まず技の優先度を比較し、同じ優先度なら素早さを比較して先攻・後攻を決める（同速なら五分五分でランダム）
    # トリックルームの間は、同じ優先度の中で素早さの遅い方が先に行動する（せんせいのツメは今まで通り先に行動できる）
    def get_attacker_and_defender(self, move1: BaseMove, move2: BaseMove):
        if move1.priority != move2.priority:
            if move1.priority > move2.priority:
                return self.pokemon1, self.pokemon2
            return self.pokemon2, self.pokemon1

        # せんせいのツメは、同じ優先度の中でだけ20%の確率で先に行動できる（両方発動した場合は素早さで比べる）
        quick_claw1 = self.pokemon1.held_item.try_move_first()
        quick_claw2 = self.pokemon2.held_item.try_move_first()
        if quick_claw1 != quick_claw2:
            if quick_claw1:
                return self.pokemon1, self.pokemon2
            return self.pokemon2, self.pokemon1

        speed1 = self.get_effective_speed(self.pokemon1)
        speed2 = self.get_effective_speed(self.pokemon2)
        # トリックルームの間は、素早さの遅い方が先に行動する
        if self.trick_room_turns_remaining > 0:
            speed1, speed2 = -speed1, -speed2
        if speed1 > speed2:
            return self.pokemon1, self.pokemon2
        if speed2 > speed1:
            return self.pokemon2, self.pokemon1
        return random.sample([self.pokemon1, self.pokemon2], 2)

    # 素早さランク・持ち物（こだわりスカーフ1.5倍・くろいてっきゅう1/2）・特性（すいすい等）・まひ(1/4)を反映した、
    # 行動順の判定に使う素早さを返す
    def get_effective_speed(self, pokemon: Pokemon) -> int:
        ability = self.get_ability(pokemon)
        speed = int(pokemon.status.spd * stage_multiplier(self.get_stages(pokemon).spd))
        speed = int(speed * pokemon.held_item.get_speed_multiplier())
        speed = int(speed * ability.get_speed_multiplier(self, pokemon))
        if pokemon.current_status.status_condition == "paralysis" and not ability.ignores_paralysis_speed_drop:
            speed = int(speed * PARALYSIS_SPEED_MULTIPLIER)
        return speed

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

    # 残りHPが0以下なら瀕死。交代でベンチに下がった後の個体にも呼べるよう、
    # get_current_hpの「今場に出ているか」チェックは経由せず直接HPを見る
    def is_fainted(self, target: Pokemon) -> bool:
        return target.current_status.current_hp <= 0

    # 天候・命中率/回避率ランクを考慮した実際の命中率を返す
    # hitrate=0は「必ず命中する」という既存の規約なので、必中にしたい場合はそのまま流用できる
    def get_effective_hitrate(self, move: BaseMove, attacker: Pokemon, defender: Pokemon) -> int:
        # ノーガード: 自分が出す技・自分が受ける技は必ず命中する
        if self.is_no_guard_active(attacker, defender):
            return 0

        weather = self.get_effective_weather()
        base_hitrate = move.hitrate
        if move.id == THUNDER_ID:
            if weather == "rain":
                base_hitrate = 0
            elif weather == "sun":
                base_hitrate = 50
        elif move.id == BLIZZARD_ID and weather == "hail":
            base_hitrate = 0

        if base_hitrate == 0:
            return 0

        # みやぶるで見破られている相手には、回避ランクを無視して命中判定する
        accuracy_stage = self.get_stages(attacker).accuracy
        if defender.current_status.is_identified:
            evasion_stage = 0
        else:
            evasion_stage = self.get_stages(defender).evasion

        combined_stage = max(-6, min(6, accuracy_stage - evasion_stage))
        effective_hitrate = base_hitrate * accuracy_stage_multiplier(combined_stage)

        # 持ち物による命中率の補正。フォーカスレンズは相手が既にこのターン行動していれば発動する
        effective_hitrate *= attacker.held_item.get_accuracy_multiplier(attacker, defender)
        effective_hitrate *= defender.held_item.get_received_accuracy_multiplier()

        # 特性による命中率の補正（はりきり・すながくれ・ゆきがくれ）
        effective_hitrate *= self.get_ability(attacker).get_accuracy_multiplier(attacker, move)
        effective_hitrate *= self.get_target_ability(defender, attacker).get_evasion_multiplier(self, defender)

        # hitrate=0は「必中」を表す既存の規約と衝突しないよう、下限を1にクランプする
        return max(1, min(100, round(effective_hitrate)))

    # attacker・defenderのどちらかがノーガードかどうか
    def is_no_guard_active(self, attacker: Pokemon, defender: Pokemon) -> bool:
        return self.get_ability(attacker).always_hits or self.get_ability(defender).always_hits

    # move.min_hits/max_hitsから今回のヒット回数を決める
    # 2〜5回攻撃(ボーンラッシュ等)は3/8, 3/8, 1/8, 1/8という第4世代仕様の確率分布、それ以外(固定回数)はそのまま使う
    def roll_hit_count(self, move: BaseMove) -> int:
        if move.min_hits == 2 and move.max_hits == 5:
            return random.choices([2, 3, 4, 5], weights=[3, 3, 1, 1])[0]
        return random.randint(move.min_hits, move.max_hits)

    # attackerがdefenderにmoveを撃つ。命中判定→(変化技でなければ)ダメージ計算・適用の順で行い、結果を返す
    # 複数回攻撃技は命中判定を1回だけ行い、そのあと決めたヒット回数分ダメージを繰り返し与える（相手が瀕死になったら打ち切り）
    def use_move(self, attacker: Pokemon, defender: Pokemon, move: BaseMove) -> dict:
        result = {"hit": False, "damage": 0, "effectiveness": 1.0, "hit_count": 0, "charging": False,
                  "blocked_by_protect": False, "blocked_by_ability": False, "blocked_by_substitute": False,
                  "hit_substitute": False}

        # 1ターン目（溜め開始）かどうか。charging_moveが同じ技を指していれば、今回は2ターン目(攻撃)
        is_releasing_charge = attacker.current_status.charging_move is move

        # 技を選んだ後、行動する前にアンコール・かなしばり・ちょうはつ・いちゃもんを受けた場合の処理
        # (わるあがきや溜め技の2ターン目のように、技構成から選んだのではない技は対象外)
        if not is_releasing_charge and any(m is move for m in attacker.moves):
            # アンコールされていれば、選んでいた技の代わりに固定された技を使う
            encore_move = attacker.current_status.encore_move
            if encore_move is not None and encore_move.current_pp > 0:
                move = encore_move
            # 使えなくなった技は失敗する（PPは減らない）
            if not self.is_move_selectable(attacker, move):
                return result

        # メトロノーム用に、同じ技を連続で使った回数を数える（溜め技の2ターン目は同じ1回の使用として数えない）
        if not is_releasing_charge:
            if attacker.current_status.last_move_used_id == move.id:
                attacker.current_status.consecutive_move_count += 1
            else:
                attacker.current_status.consecutive_move_count = 0

        # まねっこがコピーできるよう、使った技のIDを記録しておく
        attacker.current_status.last_move_used_id = move.id

        # まもる・みきり・こらえる以外の技を使ったら、連続成功カウンタをリセットする
        if move.id not in PROTECT_FAMILY_MOVE_IDS:
            attacker.current_status.protect_stall_counter = 0

        # こだわり系の持ち物を持っていれば、最初に出した技に固定される（わるあがき等、技構成に無い技は対象外）
        if attacker.held_item.locks_move and any(m is move for m in attacker.moves):
            attacker.current_status.choice_locked_move = move

        # ソーラービームは晴れの間だけ、溜めターンを省略していきなり攻撃する
        skip_charge_turn = move.id == SOLAR_BEAM_ID and self.get_effective_weather() == "sun"

        # パワフルハーブを持っていれば、1回だけ溜めターンを省略する（晴れのソーラービーム等、元々溜めない場合は消費しない）
        if (move.requires_charge_turn and not is_releasing_charge and not skip_charge_turn
                and attacker.held_item.try_skip_charge_turn(self, attacker)):
            skip_charge_turn = True

        if move.requires_charge_turn and not is_releasing_charge and not skip_charge_turn:
            # 溜めターン: PPだけ消費し、攻撃せずに次のターンに備える（あなをほる等は回避状態にもなる）
            self.consume_pp(attacker, defender, move)
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
            self.consume_pp(attacker, defender, move)

        # はかいこうせん等は命中・失敗に関わらず、使った時点で次ターンの反動硬直が確定する
        if move.requires_recharge:
            attacker.current_status.must_recharge = True

        # おきみやげ等は命中・失敗に関わらず、使った時点で自分が瀕死になる（第4世代仕様）
        if move.user_faints_on_use:
            attacker.current_status.current_hp = 0

        if move.calls_own_random_move:
            # ねごと: 自分の他の技をランダムに1つ呼び出して使う
            result = self.perform_sleep_talk(attacker, defender, result)
        elif move.is_delayed_attack:
            # みらいよち: このターンは攻撃せず、2ターン後に攻撃する
            result = self.perform_future_sight(attacker, defender, move, result)
        else:
            result = self._resolve_move_hit(attacker, defender, move, result)

        # じゅうでん状態は、でんき技を使った時点で消費される（威力2倍はダメージ計算で反映済み）
        if move.type == "でんき" and move.category != CATEGORY_STATUS:
            attacker.current_status.charge_turns_remaining = 0

        return result

    # moveのPPを1消費する。相手に向けた技で、相手がプレッシャーならさらに1消費する
    def consume_pp(self, attacker: Pokemon, defender: Pokemon, move: BaseMove):
        pp_cost = 1
        if self.get_ability(defender).increases_opponent_pp_usage and self.is_move_blocked_by_protect(move, attacker):
            pp_cost += 1
        move.current_pp = max(0, move.current_pp - pp_cost)

    # use_moveのうち、命中判定以降（回避状態・まもる・命中・ダメージ・追加効果）の処理
    def _resolve_move_hit(self, attacker: Pokemon, defender: Pokemon, move: BaseMove, result: dict) -> dict:
        # 相手に向けた技かどうか（自分自身・場に向けた変化技は、相手の回避状態やまもるの影響を受けない）
        targets_opponent = self.is_move_blocked_by_protect(move, attacker)

        # 相手が回避状態（あなをほる等で溜め中）なら、命中率に関わらず必ず外れる（ノーガードなら当たる）
        if defender.current_status.is_invulnerable and targets_opponent and not self.is_no_guard_active(attacker, defender):
            return result

        # 相手がまもる・みきりで守っていれば、命中率に関わらず技が防がれる（ほえる等、まもるを無視する技は除く）
        if defender.current_status.is_protected and targets_opponent and not move.bypasses_protect:
            result["blocked_by_protect"] = True
            return result

        # ちくでん・ふゆう・がんじょう等、相手の特性で技が無効化される（かたやぶりなら無視する）
        attacker_ability = self.get_ability(attacker)
        defender_ability = self.get_target_ability(defender, attacker)
        if targets_opponent and defender_ability.on_try_hit(self, attacker, defender, move):
            result["blocked_by_ability"] = True
            return result

        # でんじふゆう中の相手には、じめんのダメージ技が当たらない
        if targets_opponent and self.is_floating_against_ground_move(defender, move):
            return result

        # なげつける（持ち物が無い）・はきだす（たくわえていない）等、技を出せる条件を満たしていなければ失敗する
        if not move.try_execute(self, attacker, defender):
            return result

        # みがわりがいる相手には、相手に向けた変化技（ほえる・ちょうはつ等を除く）が効かず、
        # 吸収技（ギガドレイン・ゆめくい等）も失敗する（第4世代仕様）
        if targets_opponent and self.has_substitute(defender) and self.is_move_blocked_by_substitute(move, attacker):
            result["blocked_by_substitute"] = True
            return result

        if not check_hit(self.get_effective_hitrate(move, attacker, defender)):
            return result

        result["hit"] = True
        total_damage = 0

        # かわらわりはダメージを与える前に、相手の場の壁(リフレクター/ひかりのかべ)を破壊する
        if move.id == BRICK_BREAK_ID:
            defender_trainer = self.get_trainer(defender)
            defender_trainer.reflect_turns_remaining = 0
            defender_trainer.light_screen_turns_remaining = 0

        # 変化技(CATEGORY_STATUS)はダメージを与えないので、物理・特殊技の時だけダメージ計算する
        if move.category != CATEGORY_STATUS:
            screen_active = self.is_screen_active(defender, move)
            # みやぶるで見破られている、または攻撃側がきもったまなら、ノーマル/かくとう技がゴーストタイプに当たる
            ignore_ghost_immunity = defender.current_status.is_identified or attacker_ability.ignores_ghost_immunity
            effectiveness = get_move_effectiveness(move, defender, ignore_ghost_immunity)
            hit_count = self.roll_hit_count(move)
            # 最後のヒットをみがわりが受け止めたかどうか（受け止めていれば、追加効果は本体に届かない）
            last_hit_absorbed = False
            for _ in range(hit_count):
                if self.is_fainted(defender):
                    break

                # みがわりがいれば、攻撃は身代わりが受ける（複数回攻撃で途中で壊れたら、残りは本体に当たる）
                hits_substitute = self.has_substitute(defender)

                # 半減実は効果抜群の対応タイプの技を受けたときに1回だけ発動する（複数回攻撃なら最初の1回だけ）
                # みがわりが受けた攻撃では発動しない
                defender_item = defender.held_item
                received_multiplier = (1.0 if hits_substitute
                                       else defender_item.get_received_damage_multiplier(defender, move, effectiveness))

                # いかりのつぼの判定のため、急所判定はダメージ計算の外で行う
                is_critical = roll_critical(attacker, move, attacker_ability, defender_ability)
                damage = calculate_damage(
                    attacker, defender, move, self.get_effective_weather(), screen_active, ignore_ghost_immunity,
                    self.get_stages(attacker), self.get_stages(defender), received_multiplier,
                    attacker_ability, defender_ability, is_critical,
                )
                if received_multiplier != 1.0 and damage > 0:
                    defender_item.on_received_damage_reduced(self, defender)

                last_hit_absorbed = hits_substitute
                if hits_substitute:
                    # 身代わりのHPを超えた分のダメージは本体に届かない（反動・かいがらのすずは身代わりに与えた分で計算する）
                    total_damage += self.apply_substitute_damage(defender, damage)
                    result["hit_count"] += 1
                    result["hit_substitute"] = True
                    continue

                damage = self.apply_survival_effects(defender, damage)

                self.apply_damage(defender, damage)
                total_damage += damage
                result["hit_count"] += 1

                if is_critical and damage > 0 and not self.is_fainted(defender):
                    self.get_ability(defender).on_critical_hit_received(self, defender)

            result["damage"] = total_damage
            result["effectiveness"] = effectiveness

            # みちづれ・おんねん: この攻撃で相手が瀕死になったら発動する
            if result["hit_count"] > 0 and self.is_fainted(defender):
                self.apply_faint_retaliation(attacker, defender, move)

            # テクスチャー2が参照できるよう、受けた技のタイプを記録しておく（みがわりが受けた場合は本体は受けていない）
            if result["hit_count"] > 0 and not last_hit_absorbed:
                defender.current_status.last_hit_by_type = move.type

            # 身代わりが受け止めた攻撃の追加効果・持ち物の効果は、相手本体には届かない
            if last_hit_absorbed:
                self.substitute_absorbed_target = defender

            # かいがらのすず・いのちのたま・おうじゃのしるし等、ダメージを与えた後に発動する持ち物
            # (とんぼがえりで交代する前に発動させるため、追加効果より先に処理する)
            if total_damage > 0:
                self.apply_after_damage_items(attacker, defender, move, total_damage)

        # 命中していれば、技固有の追加効果を発動させる（無い技はBaseMoveのデフォルトで何もしない）
        move.apply_effect(self, attacker, defender, total_damage)
        self.substitute_absorbed_target = None

        return result

    # 瀕死になるはずの攻撃ダメージを、こらえる・きあいのタスキ・きあいのハチマキでHP1残りに抑える
    # こらえるが優先され、その場合きあいのタスキは消費しない
    def apply_survival_effects(self, defender: Pokemon, damage: int) -> int:
        current_hp = defender.current_status.current_hp
        if damage < current_hp:
            return damage

        if defender.current_status.is_enduring:
            return max(0, current_hp - 1)
        if defender.held_item.try_endure_fatal_hit(self, defender):
            return max(0, current_hp - 1)
        return damage

    # attackerがdefenderにダメージを与えた後に発動する、attacker側の持ち物の効果
    def apply_after_damage_items(self, attacker: Pokemon, defender: Pokemon, move: BaseMove, total_damage: int):
        if self.is_fainted(attacker):
            return
        attacker.held_item.on_after_damage(self, attacker, defender, move, total_damage)

    # pokemonの持ち物を消費する（きのみを食べる等）。消費した持ち物はリサイクル用にconsumed_itemに記録する
    def consume_item(self, pokemon: Pokemon):
        pokemon.consumed_item = pokemon.item
        pokemon.item = None
        # かるわざ: 持ち物を消費すると素早さが上がる
        self.get_ability(pokemon).on_item_consumed(self, pokemon)

    # 場に出ている両者について、条件を満たしていれば持ち物（きのみ・しろいハーブ）を発動させる
    def activate_held_items_on_field(self):
        for pokemon in (self.pokemon1, self.pokemon2):
            self.activate_held_items(pokemon)

    # 状態異常・残りHP・能力ランクの低下に反応して発動する持ち物の処理（きのみ・しろいハーブ。発動したら消費する）
    def activate_held_items(self, pokemon: Pokemon):
        if self.is_fainted(pokemon):
            return
        pokemon.held_item.activate(self, pokemon)

    # status_condition（どく・まひ・ねむり等）を回復する
    def cure_status(self, pokemon: Pokemon):
        pokemon.current_status.status_condition = None
        pokemon.current_status.sleep_turns_remaining = 0

    # ターン終了時の、たべのこし・くろいヘドロの回復/ダメージ
    def apply_end_of_turn_items(self):
        for pokemon in (self.pokemon1, self.pokemon2):
            if not self.is_fainted(pokemon):
                pokemon.held_item.on_end_of_turn(self, pokemon)

    # ターン終了時の最後に発動する持ち物（どくどくだま）
    def apply_end_of_turn_orbs(self):
        for pokemon in (self.pokemon1, self.pokemon2):
            if not self.is_fainted(pokemon):
                pokemon.held_item.on_end_of_turn_late(self, pokemon)

    # どちらかの手持ち全員が瀕死なら、もう片方の場のポケモンを返す。両方全滅/両方生存中ならNone
    def get_winner(self):
        trainer1_defeated = self.trainer1.is_defeated()
        trainer2_defeated = self.trainer2.is_defeated()

        if trainer1_defeated and trainer2_defeated:
            return None
        if trainer1_defeated:
            return self.pokemon2
        if trainer2_defeated:
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
    # sourceは効果の発生元。相手(source)にランクを下げられる場合は、クリアボディ等の特性で防がれる
    def try_apply_stat_change(self, target, stat_name, stage_amount, chance, source=None):
        return self.try_apply_stat_multi_change(target, [(stat_name, stage_amount)], chance, source)

    # 相手(source)によるstat_nameのランクダウンが、targetの特性で防がれるかどうか
    def is_stat_drop_prevented(self, target, stat_name, stage_amount, source) -> bool:
        if stage_amount >= 0 or source is None or source is target:
            return False
        return self.get_target_ability(target, source).prevents_stat_drop(stat_name)

    # みやぶるでtargetを「見破った」状態にする。以後、相手の回避ランクを無視して命中判定し、
    # ノーマル/かくとう技に対するゴーストタイプの無効化も無視する（対象が場を退くと解除）
    def perform_identify(self, target):
        target.current_status.is_identified = True

    # moveがまもる・みきりで防がれる対象（＝相手に向けた技）かどうかを判定する
    # (ほえるのように、相手に向けた技でもまもるを無視する技はmove.bypasses_protectで別に判定する)
    # ダメージを与える技は常に防がれる。変化技は「相手(target)」に向けた効果を持つものだけ防がれ、
    # 自分自身への効果（つるぎのまい等）や天候・設置技・壁など場に対する効果は本編仕様通り防がれない
    # のろいはゴーストタイプが使った場合だけ相手に向けた技になるため、使用者(attacker)も見て判定する
    def is_move_blocked_by_protect(self, move: BaseMove, attacker: Pokemon = None) -> bool:
        if move.category != CATEGORY_STATUS:
            return True
        return any(self.is_opponent_directed_effect(effect, attacker) for effect in move.effects)

    # 変化技の効果が「相手」に向けたものかどうか（まもる・みがわりで防がれる対象の判定に使う）
    def is_opponent_directed_effect(self, effect, attacker: Pokemon = None) -> bool:
        kind = effect[0]
        if kind in ("status", "status_random", "stat", "stat_multi", "flinch") and effect[1] == "target":
            return True
        # いたみわけ・いえき等は相手のHP・特性・技・持ち物を直接書き換えるので、相手に向けた効果として防がれる
        if kind in ("pain_split", "suppress_ability", "force_switch", "taunt", "encore", "disable", "torment",
                    "nightmare", "mean_look", "trick", "spite", "leech_seed", "yawn", "attract"):
            return True
        if kind == "curse" and attacker is not None and self.is_ghost_type(attacker):
            return True
        return False

    # 相手に向けたmoveが、みがわりで防がれるかどうか（相手にみがわりがいるかどうかは呼び出し側で判定する）
    # ダメージ技は身代わりが受ける（防がれるのではない）ので対象外だが、吸収技は第4世代仕様で失敗する
    # 変化技は、相手に向けた効果がほえる・ちょうはつ等のみがわりを無視する効果だけなら防がれない
    def is_move_blocked_by_substitute(self, move: BaseMove, attacker: Pokemon = None) -> bool:
        if move.category != CATEGORY_STATUS:
            return any(effect[0] == "drain" for effect in move.effects)
        return any(self.is_opponent_directed_effect(effect, attacker) and effect[0] not in SUBSTITUTE_BYPASS_EFFECT_KINDS
                   for effect in move.effects)

    # まもる・みきり・こらえるの連続使用による成功率の減衰を判定し、成功していればis_protected/is_enduringを立てる
    # 本編仕様: 初回100%、以降連続成功するたびに1/3倍。失敗、またはこれら以外の技を使うと0に戻る
    def attempt_protect_family_move(self, attacker: Pokemon, is_endure: bool):
        stall_count = attacker.current_status.protect_stall_counter
        success_chance = PROTECT_STALL_SUCCESS_RATIO ** stall_count

        if random.random() < success_chance:
            if is_endure:
                attacker.current_status.is_enduring = True
            else:
                attacker.current_status.is_protected = True
            attacker.current_status.protect_stall_counter = stall_count + 1
        else:
            attacker.current_status.protect_stall_counter = 0

    # まもる・みきり（このターンの間、相手の技をほぼ全て防ぐ）
    def perform_protect(self, attacker: Pokemon):
        self.attempt_protect_family_move(attacker, is_endure=False)

    # こらえる（このターンの間、瀕死になるはずの攻撃をHP1で耐える）
    def perform_endure(self, attacker: Pokemon):
        self.attempt_protect_family_move(attacker, is_endure=True)

    # chanceの確率で複数の能力ランクを同時に変える（げんしのちからのような複合効果用。1回の判定で全部まとめて適用する）
    # 特性で防がれた能力だけは変化しない
    def try_apply_stat_multi_change(self, target, stat_changes, chance, source=None):
        if self.is_shielded_by_substitute(target, source):
            return False
        if random.random() < chance:
            for stat_name, stage_amount in stat_changes:
                if self.is_stat_drop_prevented(target, stat_name, stage_amount, source):
                    continue
                self.change_stage(target, stat_name, stage_amount)
            return True
        return False

    # chanceの確率でtargetに状態異常を付与する（既に何か状態異常が付いている場合は上書きしない）
    # ねむり・こんらんは残りターン数もあわせて設定する
    # こんらんだけはstatus_conditionとは別枠で管理し、他の状態異常と重複できる（既にこんらん中なら上書きしない）
    # sourceは状態異常にした相手。めんえき等の特性で防がれる判定（かたやぶり）と、シンクロの発動に使う
    def try_apply_status(self, target, condition, chance, source=None):
        if self.is_shielded_by_substitute(target, source):
            return False
        if not self.can_receive_status(target, condition, source):
            return False

        if condition == "confusion":
            if target.current_status.confusion_turns_remaining > 0:
                return False
            if random.random() < chance:
                # 行動前に1減らしてから判定するため、実際に混乱したまま行動する1〜4ターン分+1を設定する
                target.current_status.confusion_turns_remaining = random.randint(2, 5)
                return True
            return False

        if target.current_status.status_condition is not None:
            return False
        if random.random() < chance:
            target.current_status.status_condition = condition
            if condition == "sleep":
                target.current_status.sleep_turns_remaining = random.randint(1, 3)
            self.get_ability(target).on_status_inflicted(self, target, condition, source)
            return True
        return False

    # chanceの確率でtargetをひるませる（そのターンだけ行動不能。start_battle側で判定・解除する）
    # せいしんりょくならひるまない（sourceがかたやぶりなら無視する）
    def try_apply_flinch(self, target, chance, source=None):
        if self.is_shielded_by_substitute(target, source):
            return False
        if self.get_target_ability(target, source).prevents_flinch:
            return False
        if random.random() < chance:
            target.current_status.is_flinched = True
            return True
        return False

    # attacker自身がdamageのratio分だけ反動ダメージを受ける（フレアドライブなど）
    # いしあたまなら反動を受けない
    def apply_recoil(self, attacker, damage, ratio):
        if self.get_ability(attacker).prevents_recoil:
            return
        recoil_damage = max(1, int(damage * ratio))
        self.apply_damage(attacker, recoil_damage)

    # attacker自身が最大HPのratio分だけ反動ダメージを受ける（わるあがきなど、与ダメージに依存しない反動）
    def apply_max_hp_recoil(self, attacker, ratio):
        recoil_damage = max(1, int(attacker.status.hp * ratio))
        self.apply_damage(attacker, recoil_damage)

    # attacker自身がdamageのratio分だけHPを回復する（ギガドレインなど）
    # おおきなねっこを持っていれば回復量が1.3倍になる。吸った相手(target)がヘドロえきなら、回復する代わりに同じ量のダメージを受ける
    def apply_drain(self, attacker, damage, ratio, target=None):
        heal_amount = int(damage * ratio)
        heal_amount = int(heal_amount * attacker.held_item.get_drain_multiplier())
        if target is not None and self.get_ability(target).damages_drainer:
            self.apply_damage(attacker, heal_amount)
            return
        max_hp = attacker.status.hp
        attacker.current_status.current_hp = min(max_hp, attacker.current_status.current_hp + heal_amount)

    # attacker自身が最大HPのratio分だけ回復する（じこさいせいなど）
    def apply_heal(self, attacker, ratio):
        max_hp = attacker.status.hp
        heal_amount = int(max_hp * ratio)
        attacker.current_status.current_hp = min(max_hp, attacker.current_status.current_hp + heal_amount)

    # いたみわけ: attackerとtargetの残りHPを合計し、半分(端数切り捨て)ずつ分け合う
    # 分け合った値が最大HPを超える側は最大HPまでしか回復しない
    def perform_pain_split(self, attacker: Pokemon, target: Pokemon):
        shared_hp = (attacker.current_status.current_hp + target.current_status.current_hp) // 2
        attacker.current_status.current_hp = min(attacker.status.hp, shared_hp)
        target.current_status.current_hp = min(target.status.hp, shared_hp)

    def is_ghost_type(self, pokemon: Pokemon) -> bool:
        return TYPE_ID_GHOST in (pokemon.type1, pokemon.type2)

    # はらだいこ: 最大HPの半分(端数切り捨て)を削り、攻撃ランクを最大(+6)にする
    # 残りHPが最大HPの半分以下、または既に攻撃ランクが+6なら失敗する（HPも減らない）
    def perform_belly_drum(self, attacker: Pokemon):
        max_hp = attacker.status.hp
        stages = self.get_stages(attacker)
        if attacker.current_status.current_hp <= max_hp // 2 or stages.atk >= 6:
            return
        self.apply_damage(attacker, max_hp // 2)
        stages.atk = 6

    # のろい: ゴーストタイプが使うと、自分の最大HPの半分(端数切り捨て)を削って相手をのろい状態にする
    # (自分のHPが足りなければそのまま瀕死になる。相手が既にのろい状態なら失敗しHPも減らない)
    # ゴーストタイプ以外が使うと、自分の攻撃・防御+1、素早さ-1
    def perform_curse(self, attacker: Pokemon, target: Pokemon):
        if self.is_ghost_type(attacker):
            if target.current_status.is_cursed:
                return
            self.apply_damage(attacker, max(1, attacker.status.hp // 2))
            target.current_status.is_cursed = True
        else:
            self.try_apply_stat_multi_change(attacker, [("atk", 1), ("defense", 1), ("spd", -1)], 1.0)

    # じゅうでん: 次のターンの終わりまで、でんき技の威力が2倍になる。あわせて自分の特防+1（第4世代以降）
    def perform_charge(self, attacker: Pokemon):
        attacker.current_status.charge_turns_remaining = CHARGE_DURATION
        self.change_stage(attacker, "spdef", 1)

    # 場に出ている両者のじゅうでんの残りターンを1減らす
    def tick_charge(self):
        for pokemon in (self.pokemon1, self.pokemon2):
            if pokemon.current_status.charge_turns_remaining > 0:
                pokemon.current_status.charge_turns_remaining -= 1

    # たくわえる: 自分の防御・特防+1。3回まで使え、4回目以降は失敗する（交代するとカウントは0に戻る）
    # はきだす・のみこむで元に戻せるよう、実際に上がったランク（+6で頭打ちなら上がらない）を記録しておく
    def perform_stockpile(self, attacker: Pokemon):
        status = attacker.current_status
        if status.stockpile_count >= STOCKPILE_MAX:
            return
        status.stockpile_count += 1
        stages = self.get_stages(attacker)
        defense_before, spdef_before = stages.defense, stages.spdef
        self.try_apply_stat_multi_change(attacker, [("defense", 1), ("spdef", 1)], 1.0)
        status.stockpile_defense_boost += stages.defense - defense_before
        status.stockpile_spdef_boost += stages.spdef - spdef_before

    # はきだす・のみこむの後、たくわえた回数を0に戻し、たくわえるで上がった防御・特防のランクを元に戻す
    def release_stockpile(self, attacker: Pokemon):
        status = attacker.current_status
        self.change_stage(attacker, "defense", -status.stockpile_defense_boost)
        self.change_stage(attacker, "spdef", -status.stockpile_spdef_boost)
        status.stockpile_count = 0
        status.stockpile_defense_boost = 0
        status.stockpile_spdef_boost = 0

    # のみこむ: たくわえた回数に応じて回復し（1回: 1/4、2回: 1/2、3回: 全回復）、たくわえた効果を解除する
    # (たくわえていなければ技自体が失敗する。BaseMove.try_executeで判定済み)
    def perform_swallow(self, attacker: Pokemon):
        self.apply_heal(attacker, SWALLOW_HEAL_RATIOS[attacker.current_status.stockpile_count])
        self.release_stockpile(attacker)

    # いえき: targetの特性を消す（交代するまで）。消されている間、get_abilityは「特性なし」(NO_ABILITY)を返す
    def perform_suppress_ability(self, target: Pokemon):
        target.current_status.is_ability_suppressed = True

    # まねっこ: targetが直前に使った技を、attackerの技構成の中のmimic_move(まねっこ自身)の枠にコピーする
    # コピーした技のPPは固定5。targetがまだ技を使っていない場合や、コピー不可の技(わるあがき)なら失敗する
    # 注意: 交代して元のまねっこに戻す処理はまだ実装していない
    def perform_mimic(self, attacker: Pokemon, target: Pokemon, mimic_move: BaseMove):
        last_move_id = target.current_status.last_move_used_id
        if last_move_id is None or last_move_id == STRUGGLE_ID:
            return

        for index, move in enumerate(attacker.moves):
            if move is mimic_move:
                copied_move = create_move(last_move_id)
                copied_move.pp = COPIED_MOVE_PP
                copied_move.current_pp = COPIED_MOVE_PP
                attacker.moves[index] = copied_move
                break

    # ものまね: attackerがtargetに変身する。タイプ・実数値(HPを除く)・技構成(各PP5)・特性をコピーする
    # 現在HP・状態異常・持ち物はコピーしない
    # 注意: 交代して元の姿に戻す処理はまだ実装していない
    def perform_transform(self, attacker: Pokemon, target: Pokemon):
        attacker.type1 = target.type1
        attacker.type2 = target.type2
        # 特性ごとの状態（もらいびの発動済み等）は引き継がず、同じ特性の新しいインスタンスを持つ
        attacker.ability = create_ability(target.ability.id)

        attacker.status = PokemonStatus(
            hp=attacker.status.hp,  # HPは変身前のまま変わらない
            atk=target.status.atk,
            defense=target.status.defense,
            spatk=target.status.spatk,
            spdef=target.status.spdef,
            spd=target.status.spd,
        )
        # 実数値ごと置き換えるので、変身前のパワートリックの入れ替えは無くなる（相手の入れ替え後の実数値をコピーする）
        attacker.current_status.is_power_trick_active = False

        copied_moves = []
        for move in target.moves:
            copied_move = create_move(move.id)
            copied_move.pp = COPIED_MOVE_PP
            copied_move.current_pp = COPIED_MOVE_PP
            copied_moves.append(copied_move)
        attacker.moves = copied_moves

    # とんぼがえり: 攻撃したpokemon自身が、手持ちの生きている次の1体に強制的に交代する
    # (プレイヤー判断が無いので、resolve_faintsと同じ選び方＝手持ち順で最初に見つかった生存個体にする)
    # 手持ちに他に生きている個体がいなければ何もしない（交代せず攻撃だけで終わる）
    def perform_self_switch(self, pokemon: Pokemon):
        trainer = self.get_trainer(pokemon)
        next_index = trainer.find_next_alive_index()
        if next_index is None:
            return
        self.switch_in(trainer, next_index)

    # テクスチャー2: 直前に受けた技のタイプを半減または無効にするタイプの中から1つ選び、単一タイプに変わる
    # (現在自分が持っているタイプは候補から除く)。まだ何も技を受けていない、外れた技しか受けていない、
    # 候補が無い場合は失敗する
    def perform_type_change_resist(self, attacker: Pokemon):
        hit_type = attacker.current_status.last_hit_by_type
        if hit_type is None:
            return

        current_types = {attacker.type1, attacker.type2}
        candidates = []
        for type_id_str in load_type_data():
            type_id = int(type_id_str)
            if type_id in current_types:
                continue
            if get_multiplier(hit_type, type_id) <= 0.5:
                candidates.append(type_id)

        if not candidates:
            return

        attacker.type1 = random.choice(candidates)
        attacker.type2 = None

    # ---- 交代・拘束・特殊なターン管理が必要な効果 ----

    # 場を退くpokemonの、交代・拘束・技の制限に関する状態を解除する
    def clear_volatile_statuses(self, pokemon: Pokemon):
        status = pokemon.current_status
        status.stockpile_defense_boost = 0
        status.stockpile_spdef_boost = 0
        status.bound_turns_remaining = 0
        status.bound_by = None
        status.trapped_by = None
        status.taunt_turns_remaining = 0
        status.encore_move = None
        status.encore_turns_remaining = 0
        status.disabled_move = None
        status.disable_turns_remaining = 0
        status.is_tormented = False
        status.has_nightmare = False
        status.is_destiny_bond_active = False
        status.is_grudge_active = False
        status.magnet_rise_turns_remaining = 0
        status.substitute_hp = 0
        status.is_ingrained = False
        status.has_aqua_ring = False
        status.is_seeded = False
        status.yawn_turns_remaining = 0
        status.perish_turns_remaining = 0
        status.infatuated_by = None
        # パワートリックで入れ替えた攻撃と防御の実数値を元に戻す
        if status.is_power_trick_active:
            self.perform_power_trick(pokemon)

    # 場に出ている両者の、ちょうはつ・アンコール・かなしばり・でんじふゆう・あくびの残りターンを1減らす
    # あくびの残りターンが0になったら、その時点でねむり状態にする（既に他の状態異常になっていればねむらない）
    def tick_volatile_statuses(self):
        for pokemon in (self.pokemon1, self.pokemon2):
            status = pokemon.current_status
            if status.taunt_turns_remaining > 0:
                status.taunt_turns_remaining -= 1
            if status.encore_turns_remaining > 0:
                status.encore_turns_remaining -= 1
                if status.encore_turns_remaining <= 0:
                    status.encore_move = None
            if status.disable_turns_remaining > 0:
                status.disable_turns_remaining -= 1
                if status.disable_turns_remaining <= 0:
                    status.disabled_move = None
            if status.magnet_rise_turns_remaining > 0:
                status.magnet_rise_turns_remaining -= 1
            if status.yawn_turns_remaining > 0:
                status.yawn_turns_remaining -= 1
                if status.yawn_turns_remaining <= 0 and not self.is_fainted(pokemon):
                    self.try_apply_status(pokemon, "sleep", 1.0)

    # pokemonが直前に使った技を、技構成の中から探す（まだ技を使っていない、わるあがき・コピーで消えた技ならNone）
    def find_last_used_move(self, pokemon: Pokemon):
        last_move_id = pokemon.current_status.last_move_used_id
        if last_move_id is None:
            return None
        for move in pokemon.moves:
            if move.id == last_move_id:
                return move
        return None

    # でんじふゆう中で、moveがじめんのダメージ技なら当たらない（くろいてっきゅうを持っていれば当たる）
    def is_floating_against_ground_move(self, defender: Pokemon, move: BaseMove) -> bool:
        if move.is_typeless or move.type != "じめん" or move.category == CATEGORY_STATUS:
            return False
        return defender.current_status.magnet_rise_turns_remaining > 0 and not defender.is_forced_grounded

    # pokemonが持ち物を失った（消費以外で手放した）ときの処理。かるわざは、はたきおとす・トリックで持ち物を失っても発動する
    def on_item_lost(self, pokemon: Pokemon):
        self.get_ability(pokemon).on_item_consumed(self, pokemon)

    # みちづれ・おんねん: attackerの攻撃でdefenderが瀕死になったとき、defenderがみちづれ状態ならattackerも瀕死になり、
    # おんねん状態ならattackerがその攻撃に使った技のPPが0になる
    def apply_faint_retaliation(self, attacker: Pokemon, defender: Pokemon, move: BaseMove):
        status = defender.current_status
        if status.is_destiny_bond_active:
            attacker.current_status.current_hp = 0
        if status.is_grudge_active:
            move.current_pp = 0
        status.is_destiny_bond_active = False
        status.is_grudge_active = False

    # みちづれ: 次に自分が行動しようとするまでの間に、相手の攻撃で瀕死になると相手も瀕死にする
    def perform_destiny_bond(self, attacker: Pokemon):
        attacker.current_status.is_destiny_bond_active = True

    # おんねん: 次に自分が行動しようとするまでの間に、相手の攻撃で瀕死になるとその技のPPを0にする
    def perform_grudge(self, attacker: Pokemon):
        attacker.current_status.is_grudge_active = True

    # はたきおとす: 相手の持ち物をはたき落とす（対戦中は戻らず、リサイクルでも取り戻せない）。ねんちゃくなら落とせない
    def perform_knock_off(self, attacker: Pokemon, target: Pokemon):
        if self.is_shielded_by_substitute(target, attacker):
            return
        if target.item is None or self.get_target_ability(target, attacker).prevents_item_removal:
            return
        target.item = None
        self.on_item_lost(target)

    # トリック: 自分と相手の持ち物を入れ替える。両者とも持ち物が無い、または相手がねんちゃくなら失敗する
    # 入れ替えた後は、こだわり系の持ち物による技の固定を解除する（受け取った側は次に使った技に固定される）
    def perform_trick(self, attacker: Pokemon, target: Pokemon):
        if attacker.item is None and target.item is None:
            return
        if self.get_target_ability(target, attacker).prevents_item_removal:
            return
        attacker.item, target.item = target.item, attacker.item
        for pokemon in (attacker, target):
            pokemon.current_status.choice_locked_move = None
            if pokemon.item is None:
                self.on_item_lost(pokemon)

    # リサイクル: 最後に消費した持ち物を取り戻す。持ち物を持っている、または消費した持ち物が無ければ失敗する
    def perform_recycle(self, attacker: Pokemon):
        if attacker.item is not None or attacker.consumed_item is None:
            return
        attacker.item = attacker.consumed_item
        attacker.consumed_item = None

    # なげつける: 投げつけた持ち物（技を出した時点で手放し済み）の追加効果を、相手に与える
    # (きのみ・しろいハーブは相手が食べた・使った扱いになり、どくどくだまはどく、おうじゃのしるし・するどいキバはひるませる)
    def apply_flung_item_effect(self, target: Pokemon, item, source: Pokemon):
        if item is None or self.is_fainted(target) or self.is_shielded_by_substitute(target, source):
            return
        item.on_flung(self, target, source)

    # しめつけ系の技（まきつく・すなじごく・うずしお）: 相手を2〜5ターン（ねばりのかぎづめなら5ターン）締め付ける
    # 既に締め付けられていれば、ターン数は延長しない
    def perform_bind(self, attacker: Pokemon, target: Pokemon):
        status = target.current_status
        if self.is_fainted(target) or status.bound_turns_remaining > 0 or self.is_shielded_by_substitute(target, attacker):
            return
        turns = random.choices([2, 3, 4, 5], weights=[3, 3, 1, 1])[0]
        status.bound_turns_remaining = attacker.held_item.get_binding_turns(turns)
        status.bound_by = attacker

    # くろいまなざし: 相手を逃げられなくする（使ったポケモンが場を退くまで）。既に逃げられない状態なら失敗する
    # 注意: 交代はプレイヤーの判断ではなく瀕死時・とんぼがえり等による自動交代のみなので、今は実質的な効果は無い
    # (とんぼがえり・バトンタッチ・ほえるによる交代は、第4世代仕様でも防げない)
    def perform_mean_look(self, attacker: Pokemon, target: Pokemon):
        if target.current_status.trapped_by is not None:
            return
        target.current_status.trapped_by = attacker

    # pokemonが自分の意思で交代できない状態か（くろいまなざし・しめつけ系の技・ねをはる）。手動で交代する仕組みを作る時に使う
    def is_trapped(self, pokemon: Pokemon) -> bool:
        status = pokemon.current_status
        return status.trapped_by is not None or status.bound_turns_remaining > 0 or status.is_ingrained

    # ほえる: 相手を強制的に交代させる。交代先は手持ちの生きている個体からランダムに選ぶ
    # 交代できる個体がいない、相手がきゅうばん、またはねをはるで根を張っていれば失敗する
    def perform_force_switch(self, attacker: Pokemon, target: Pokemon):
        if self.is_fainted(target) or self.get_target_ability(target, attacker).prevents_forced_switch:
            return
        if target.current_status.is_ingrained:
            return
        trainer = self.get_trainer(target)
        candidates = [index for index, pokemon in enumerate(trainer.party)
                      if index != trainer.active_index and not self.is_fainted(pokemon)]
        if not candidates:
            return
        self.switch_in(trainer, random.choice(candidates))

    # バトンタッチ: 能力ランク等を引き継いで、手持ちの生きている次の1体に交代する（いなければ失敗）
    def perform_baton_pass(self, pokemon: Pokemon):
        trainer = self.get_trainer(pokemon)
        next_index = trainer.find_next_alive_index()
        if next_index is None:
            return
        self.switch_in(trainer, next_index, baton_pass=True)

    # ちょうはつ: 相手を3〜5ターンの間、変化技を使えなくする。既にちょうはつ状態なら失敗する
    def perform_taunt(self, target: Pokemon):
        if target.current_status.taunt_turns_remaining > 0:
            return
        target.current_status.taunt_turns_remaining = random.randint(*TAUNT_TURNS_RANGE)

    # アンコール: 相手が直前に使った技を、4〜8ターンの間それしか出せなくする
    # 既にアンコール状態、まだ技を使っていない、その技のPPが無い、固定できない技（アンコール・まねっこ・ものまね・
    # わるあがき）なら失敗する
    def perform_encore(self, target: Pokemon):
        status = target.current_status
        if status.encore_move is not None:
            return
        move = self.find_last_used_move(target)
        if move is None or move.current_pp <= 0 or move.id == ENCORE_ID:
            return
        if any(effect[0] in ("mimic", "transform") for effect in move.effects):
            return
        status.encore_move = move
        status.encore_turns_remaining = random.randint(*ENCORE_TURNS_RANGE)

    # かなしばり: 相手が直前に使った技を、4〜7ターンの間使えなくする
    # 既にかなしばり状態、まだ技を使っていない、その技のPPが無いなら失敗する
    def perform_disable(self, target: Pokemon):
        status = target.current_status
        if status.disabled_move is not None:
            return
        move = self.find_last_used_move(target)
        if move is None or move.current_pp <= 0:
            return
        status.disabled_move = move
        status.disable_turns_remaining = random.randint(*DISABLE_TURNS_RANGE)

    # いちゃもん: 相手が同じ技を2回続けて出せなくする（交代するまで）。既にいちゃもん状態なら失敗する
    def perform_torment(self, target: Pokemon):
        target.current_status.is_tormented = True

    # あくむ: ねむっている相手を、ねむっている間毎ターン最大HPの1/4ずつ削る状態にする
    # 相手がねむっていない、または既にあくむ状態なら失敗する
    def perform_nightmare(self, target: Pokemon):
        status = target.current_status
        if status.status_condition != "sleep" or status.has_nightmare:
            return
        status.has_nightmare = True

    # うらみ: 相手が直前に使った技のPPを4減らす。まだ技を使っていない、その技のPPが無いなら失敗する
    def perform_spite(self, target: Pokemon):
        move = self.find_last_used_move(target)
        if move is None or move.current_pp <= 0:
            return
        move.current_pp = max(0, move.current_pp - SPITE_PP_REDUCTION)

    # でんじふゆう: 5ターンの間、じめん技・まきびし・どくびしを受けなくなる。既に浮いている、またはねをはるで根を張っていれば失敗する
    def perform_magnet_rise(self, attacker: Pokemon):
        if attacker.current_status.magnet_rise_turns_remaining > 0 or attacker.current_status.is_ingrained:
            return
        attacker.current_status.magnet_rise_turns_remaining = MAGNET_RISE_DURATION

    # ねごと: ねむっている間だけ使え、自分の他の技からランダムに1つ選んで使う（呼び出した技のPPは減らない）
    # ねごと自身・溜め技・きあいパンチ等は呼び出せない。ねむっていない、または呼び出せる技が無ければ失敗する
    def perform_sleep_talk(self, attacker: Pokemon, defender: Pokemon, result: dict) -> dict:
        if attacker.current_status.status_condition != "sleep":
            return result
        candidates = [move for move in attacker.moves
                      if not move.cannot_be_called_by_sleep_talk and not move.requires_charge_turn]
        if not candidates:
            return result

        called_move = random.choice(candidates)
        if called_move.requires_recharge:
            attacker.current_status.must_recharge = True
        if called_move.user_faints_on_use:
            attacker.current_status.current_hp = 0
        if called_move.is_delayed_attack:
            return self.perform_future_sight(attacker, defender, called_move, result)
        return self._resolve_move_hit(attacker, defender, called_move, result)

    # みらいよち: 使ったターンを含めて3回目のターン終了時に、相手の場に出ているポケモンを攻撃する
    # 第4世代仕様で、ダメージは使った時点の能力で計算し（タイプなし扱いで相性・タイプ一致の影響を受けず、急所にも当たらない）、
    # 命中判定は攻撃する時に行う。相手の場に既にみらいよちが向けられていれば失敗する
    def perform_future_sight(self, attacker: Pokemon, defender: Pokemon, move: BaseMove, result: dict) -> dict:
        trainer = self.get_trainer(defender)
        if trainer.future_sight_turns_remaining > 0:
            return result

        damage = calculate_damage(
            attacker, defender, move, self.get_effective_weather(), self.is_screen_active(defender, move), False,
            self.get_stages(attacker), self.get_stages(defender), 1.0,
            self.get_ability(attacker), self.get_target_ability(defender, attacker), is_critical=False,
        )
        trainer.future_sight_turns_remaining = FUTURE_SIGHT_DELAY
        trainer.future_sight_damage = damage
        trainer.future_sight_hitrate = move.hitrate
        result["hit"] = True
        return result

    # ターン終了時、みらいよちの残りターンを1減らし、0になったらその時点で場に出ている個体を攻撃する
    def apply_future_sight(self):
        for trainer in (self.trainer1, self.trainer2):
            if trainer.future_sight_turns_remaining <= 0:
                continue
            trainer.future_sight_turns_remaining -= 1
            if trainer.future_sight_turns_remaining > 0:
                continue

            target = trainer.active
            if self.is_fainted(target) or not check_hit(trainer.future_sight_hitrate):
                continue
            damage = self.apply_survival_effects(target, trainer.future_sight_damage)
            self.apply_damage(target, damage)

    # ---- みがわり・じこあんじ・パワートリック ----

    # pokemonの前に身代わりがいるかどうか
    def has_substitute(self, pokemon: Pokemon) -> bool:
        return pokemon.current_status.substitute_hp > 0

    # 相手(source)からtargetへの効果（状態異常・能力ランクダウン・ひるみ・はたきおとす等）が、みがわりで防がれるかどうか
    # 身代わりがいる間に加え、今処理している攻撃を身代わりが受け止めた場合（その攻撃で壊れた場合を含む）も防ぐ
    # いかく等の特性も、効果の発生元(source)が相手なら防がれる
    def is_shielded_by_substitute(self, target: Pokemon, source: Pokemon = None) -> bool:
        if source is None or source is target:
            return False
        return self.has_substitute(target) or target is self.substitute_absorbed_target

    # みがわり: 最大HPの1/4（端数切り捨て）を払って、そのHPを持つ身代わりを作る
    # 既に身代わりがいる、残りHPが払うHP以下（使うと瀕死になる）、払うHPが0（最大HP1のヌケニン等）なら失敗する
    def perform_substitute(self, attacker: Pokemon):
        status = attacker.current_status
        cost = int(attacker.status.hp * SUBSTITUTE_HP_RATIO)
        if self.has_substitute(attacker) or cost <= 0 or status.current_hp <= cost:
            return
        self.apply_damage(attacker, cost)
        status.substitute_hp = cost

    # 身代わりにdamageを与え、実際に身代わりが受けたダメージ（身代わりの残りHPが上限）を返す。残りHPが0になると身代わりは壊れる
    def apply_substitute_damage(self, target: Pokemon, damage: int) -> int:
        status = target.current_status
        absorbed = min(damage, status.substitute_hp)
        status.substitute_hp -= absorbed
        return absorbed

    # じこあんじ: targetの能力ランク（命中率・回避率を含む）を、そのままattackerにコピーする
    # (まもる・みがわりに防がれない。第4世代仕様で、急所ランクはコピーしない)
    def perform_psych_up(self, attacker: Pokemon, target: Pokemon):
        copied = StatStages(**vars(self.get_stages(target)))
        if attacker is self.pokemon1:
            self.stages1 = copied
        else:
            self.stages2 = copied

    # パワートリック: pokemonの攻撃と防御の実数値を入れ替える。もう一度使うと元に戻る
    # 能力ランクは入れ替えない。入れ替えた状態は交代すると元に戻る（バトンタッチでは引き継ぐ）
    def perform_power_trick(self, pokemon: Pokemon):
        status = pokemon.status
        status.atk, status.defense = status.defense, status.atk
        pokemon.current_status.is_power_trick_active = not pokemon.current_status.is_power_trick_active

    # ---- 毎ターンの回復・吸収（ねをはる・アクアリング・やどりぎのタネ） ----

    # pokemonのHPをamountだけ回復する（最大HPを超えない）
    def restore_hp(self, pokemon: Pokemon, amount: int):
        pokemon.current_status.current_hp = min(pokemon.status.hp, pokemon.current_status.current_hp + amount)

    # ねをはる: 根を張り、毎ターン終了時に最大HPの1/16を回復する。自分の意思で交代できず、ほえるも受けなくなり、
    # 地面にいる扱いになる（ひこうタイプ・ふゆうでもじめん技が当たる）。既に根を張っていれば失敗する
    def perform_ingrain(self, attacker: Pokemon):
        attacker.current_status.is_ingrained = True

    # アクアリング: 毎ターン終了時に最大HPの1/16を回復する。既にアクアリングを張っていれば失敗する
    def perform_aqua_ring(self, attacker: Pokemon):
        attacker.current_status.has_aqua_ring = True

    # やどりぎのタネ: 相手に種を植え、毎ターン終了時に相手の最大HPの1/8を奪って自分の場のポケモンを回復する
    # くさタイプ、既に種を植えられている相手には失敗する（みがわり・まもるで防がれる）
    def perform_leech_seed(self, target: Pokemon):
        if self.is_fainted(target) or TYPE_ID_GRASS in (target.type1, target.type2):
            return
        target.current_status.is_seeded = True

    # ターン終了時の、アクアリング・ねをはるの回復（おおきなねっこを持っていれば回復量1.3倍）
    def apply_end_of_turn_recovery(self):
        for pokemon in (self.pokemon1, self.pokemon2):
            if self.is_fainted(pokemon):
                continue
            status = pokemon.current_status
            multiplier = pokemon.held_item.get_drain_multiplier()
            if status.has_aqua_ring:
                self.restore_hp(pokemon, max(1, int(int(pokemon.status.hp * AQUA_RING_HEAL_RATIO) * multiplier)))
            if status.is_ingrained:
                self.restore_hp(pokemon, max(1, int(int(pokemon.status.hp * INGRAIN_HEAL_RATIO) * multiplier)))

    # ターン終了時の、やどりぎのタネの吸収。種を植えられた側が最大HPの1/8（残りHPが上限）を失い、
    # 同じ量だけ相手の場のポケモンが回復する（おおきなねっこなら1.3倍。植えられた側がヘドロえきなら、回復する代わりにダメージを受ける）
    # 種を植えた個体が交代していても、今相手の場に出ている個体が回復する
    def apply_end_of_turn_leech_seed(self):
        for pokemon in (self.pokemon1, self.pokemon2):
            if not pokemon.current_status.is_seeded or self.is_fainted(pokemon):
                continue
            receiver = self.get_opponent(pokemon)
            drained = min(pokemon.current_status.current_hp, max(1, int(pokemon.status.hp * LEECH_SEED_DRAIN_RATIO)))
            self.apply_damage(pokemon, drained)
            if self.is_fainted(receiver):
                continue
            amount = int(drained * receiver.held_item.get_drain_multiplier())
            if self.get_ability(pokemon).damages_drainer:
                self.apply_damage(receiver, amount)
            else:
                self.restore_hp(receiver, amount)

    # ---- あくび・ほろびのうた・メロメロ ----

    # あくび: 相手をねむけ状態にし、次のターンの終わりにねむらせる
    # 相手が既に状態異常・ねむけ状態、またはねむり状態にならない（ふみん等。かたやぶりなら無視）なら失敗する
    # (みがわり・まもるで防がれる)
    def perform_yawn(self, attacker: Pokemon, target: Pokemon):
        status = target.current_status
        if self.is_fainted(target) or status.status_condition is not None or status.yawn_turns_remaining > 0:
            return
        if not self.can_receive_status(target, "sleep", attacker):
            return
        status.yawn_turns_remaining = YAWN_DURATION

    # ほろびのうた: 使った本人を含む場の全員に、ほろびのカウントを付ける（カウント0になったターンの終わりに瀕死）
    # 既にカウントがある個体はカウントし直さない。使った本人以外は、ぼうおんで防げる（かたやぶりなら無視）
    # まもる・みがわりには防がれない
    def perform_perish_song(self, attacker: Pokemon, move: BaseMove):
        for pokemon in (attacker, self.get_opponent(attacker)):
            status = pokemon.current_status
            if self.is_fainted(pokemon) or status.perish_turns_remaining > 0:
                continue
            if pokemon is not attacker and self.get_target_ability(pokemon, attacker).on_try_hit(self, attacker, pokemon, move):
                continue
            status.perish_turns_remaining = PERISH_SONG_DURATION

    # ターン終了時、ほろびのうたのカウントを1減らし、0になった個体を瀕死にする
    def apply_perish_song(self):
        for pokemon in (self.pokemon1, self.pokemon2):
            status = pokemon.current_status
            if status.perish_turns_remaining <= 0 or self.is_fainted(pokemon):
                continue
            status.perish_turns_remaining -= 1
            if status.perish_turns_remaining <= 0:
                status.current_hp = 0

    # メロメロ: 性別が違う相手をメロメロ状態にし、行動するたびに1/2の確率で動けなくする
    # どちらかが性別不明、同じ性別、相手が既にメロメロ状態、またはどんかん（かたやぶりなら無視）なら失敗する
    # (みがわり・まもるで防がれる)
    def perform_attract(self, attacker: Pokemon, target: Pokemon):
        if attacker.gender is None or target.gender is None or attacker.gender == target.gender:
            return
        if target.current_status.infatuated_by is not None:
            return
        if self.get_target_ability(target, attacker).prevents_infatuation:
            return
        target.current_status.infatuated_by = attacker

    # ---- トリックルーム・つぼをつく ----

    # トリックルーム: 使ったターンを含めて5ターンの間、同じ優先度の中で素早さの遅い順に行動する。効果中に使うと解除される
    def perform_trick_room(self):
        if self.trick_room_turns_remaining > 0:
            self.trick_room_turns_remaining = 0
        else:
            self.trick_room_turns_remaining = TRICK_ROOM_DURATION

    # トリックルームの残りターンを1減らす
    def tick_trick_room(self):
        if self.trick_room_turns_remaining > 0:
            self.trick_room_turns_remaining -= 1

    # つぼをつく: 攻撃・防御・特攻・特防・素早さ・命中率・回避率のうち、+6でないものからランダムに1つ選んでランクを+2する
    # 全て+6なら失敗する。第4世代仕様で、自分にみがわりがいると失敗する
    def perform_acupressure(self, attacker: Pokemon):
        if self.has_substitute(attacker):
            return
        stages = self.get_stages(attacker)
        candidates = [stat for stat in ACUPRESSURE_STATS if getattr(stages, stat) < 6]
        if not candidates:
            return
        self.change_stage(attacker, random.choice(candidates), ACUPRESSURE_STAGES)

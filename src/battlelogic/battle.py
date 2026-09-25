import random

from battlelogic.accuracy import check_hit
from battlelogic.damage import calculate_confusion_damage, calculate_damage
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
            if self.can_act(first_mover):
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

            if self.can_act(second_mover):
                self.use_move(second_mover, current_opponent, second_move)
            second_mover.current_status.has_moved_this_turn = True
            self.activate_held_items_on_field()
            self.resolve_faints()
            if self.is_battle_over():
                break

            # 毎ターン終了時のどく・やけど・天候ダメージ、天候の経過処理
            self.apply_end_of_turn_status_damage()
            self.activate_held_items_on_field()
            self.resolve_faints()
            if self.is_battle_over():
                break

            self.apply_end_of_turn_weather_damage()
            # たべのこし・くろいヘドロの回復/ダメージ
            self.apply_end_of_turn_items()
            self.tick_weather()
            self.tick_screens()
            self.tick_charge()
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
    def resolve_faints(self):
        for trainer in (self.trainer1, self.trainer2):
            while self.is_fainted(trainer.active) and not trainer.is_defeated():
                next_index = trainer.find_next_alive_index()
                if next_index is None:
                    break
                self.switch_in(trainer, next_index)

    # trainerの場のポケモンをnew_indexの個体に交代させる。能力ランクをリセットし、設置技の効果を適用する
    def switch_in(self, trainer: Trainer, new_index: int):
        # みやぶるの「見破られた」状態、まもる・みきり・こらえるの連続成功カウンタは、場を退くと解除される
        outgoing_status = trainer.active.current_status
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

        trainer.active_index = new_index
        if trainer is self.trainer1:
            self.stages1 = StatStages()
        else:
            self.stages2 = StatStages()
        self.apply_entry_hazards(trainer)
        # どくびしでどくになった直後にラムのみで回復する、といった持ち物の発動
        if not self.is_fainted(trainer.active):
            self.activate_held_items(trainer.active)

    # trainerが持つ罠(ステルスロック・まきびし・どくびし)を、今場に出ている個体に適用する
    def apply_entry_hazards(self, trainer: Trainer):
        pokemon = trainer.active
        if self.is_fainted(pokemon):
            return

        # ひこうタイプは地面にいないので、まきびし・どくびしを受けない（くろいてっきゅうを持っていれば受ける）
        is_grounded = pokemon.held_item.forces_grounded or TYPE_ID_FLYING not in (pokemon.type1, pokemon.type2)

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
            elif pokemon.current_status.status_condition is None:
                # 本来は2層で「もうどく」（悪化していくどく）になるが、簡略化して通常のどく扱いにしている
                pokemon.current_status.status_condition = "poison"

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

        # こんらんはstatus_conditionとは別枠なので、どく・まひ等と重複していても判定する
        # 残りターンが尽きていれば、このターンの行動前に解ける
        if status.confusion_turns_remaining > 0:
            status.confusion_turns_remaining -= 1
            if status.confusion_turns_remaining > 0 and random.random() < CONFUSION_SELF_HIT_CHANCE:
                self.apply_damage(pokemon, calculate_confusion_damage(pokemon, self.get_stages(pokemon)))
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
            if condition == "poison":
                damage = max(1, int(pokemon.status.hp * POISON_DAMAGE_RATIO))
                self.apply_damage(pokemon, damage)
            elif condition == "burn":
                damage = max(1, int(pokemon.status.hp * BURN_DAMAGE_RATIO))
                self.apply_damage(pokemon, damage)

            # のろい状態なら、どく・やけどとは別に最大HPの1/4を失う
            if pokemon.current_status.is_cursed and not self.is_fainted(pokemon):
                damage = max(1, int(pokemon.status.hp * CURSE_DAMAGE_RATIO))
                self.apply_damage(pokemon, damage)

    # 天候を変える（5ターン継続）。にほんばれ・あまごい・すなあらし・あられから呼ばれる
    # 使ったポケモンが対応する岩（あついいわ・しめったいわ・つめたいいわ）を持っていれば8ターン継続する
    def set_weather(self, weather, user: Pokemon = None):
        self.weather = weather
        self.weather_turns_remaining = WEATHER_DURATION
        if user is not None:
            self.weather_turns_remaining = user.held_item.get_weather_duration(weather, WEATHER_DURATION)

    # 天候の残りターンを1減らし、0になったら天候を晴天(なし)に戻す
    def tick_weather(self):
        if self.weather is None:
            return
        self.weather_turns_remaining -= 1
        if self.weather_turns_remaining <= 0:
            self.weather = None

    # すなあらし・あられの間、免疫タイプ以外に毎ターン終了時ダメージを与える
    def apply_end_of_turn_weather_damage(self):
        immune_type_ids = WEATHER_IMMUNE_TYPE_IDS.get(self.weather)
        if immune_type_ids is None:
            return

        for pokemon in (self.pokemon1, self.pokemon2):
            if self.is_fainted(pokemon):
                continue
            if pokemon.type1 in immune_type_ids or pokemon.type2 in immune_type_ids:
                continue
            damage = max(1, int(pokemon.status.hp * WEATHER_DAMAGE_RATIO))
            self.apply_damage(pokemon, damage)

    # ここ
    # attackerが持つ技のうちPPが残っているものからランダムに1つ選ぶ。全て0ならわるあがきを選ぶ
    # 溜め中（ソーラービーム等の1ターン目を終えた状態）なら、選択せず溜めていた技を強制的に返す
    def select_move(self, attacker: Pokemon) -> BaseMove:
        if attacker.current_status.charging_move is not None:
            return attacker.current_status.charging_move

        # こだわり系の持ち物で技が固定されていれば、その技しか選べない（PPが尽きたらわるあがき）
        # まねっこ等で固定された技が技構成から消えていれば、固定を解除する
        locked_move = attacker.current_status.choice_locked_move
        if locked_move is not None:
            if any(move is locked_move for move in attacker.moves):
                return locked_move if locked_move.current_pp > 0 else Struggle()
            attacker.current_status.choice_locked_move = None

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

        # せんせいのツメは、同じ優先度の中でだけ20%の確率で先に行動できる（両方発動した場合は素早さで比べる）
        quick_claw1 = self.pokemon1.held_item.try_move_first()
        quick_claw2 = self.pokemon2.held_item.try_move_first()
        if quick_claw1 != quick_claw2:
            if quick_claw1:
                return self.pokemon1, self.pokemon2
            return self.pokemon2, self.pokemon1

        speed1 = self.get_effective_speed(self.pokemon1)
        speed2 = self.get_effective_speed(self.pokemon2)
        if speed1 > speed2:
            return self.pokemon1, self.pokemon2
        if speed2 > speed1:
            return self.pokemon2, self.pokemon1
        return random.sample([self.pokemon1, self.pokemon2], 2)

    # 素早さランク・持ち物（こだわりスカーフ1.5倍・くろいてっきゅう1/2）・まひ(1/4)を反映した、行動順の判定に使う素早さを返す
    def get_effective_speed(self, pokemon: Pokemon) -> int:
        speed = int(pokemon.status.spd * stage_multiplier(self.get_stages(pokemon).spd))
        speed = int(speed * pokemon.held_item.get_speed_multiplier())
        if pokemon.current_status.status_condition == "paralysis":
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
        base_hitrate = move.hitrate
        if move.id == THUNDER_ID:
            if self.weather == "rain":
                base_hitrate = 0
            elif self.weather == "sun":
                base_hitrate = 50
        elif move.id == BLIZZARD_ID and self.weather == "hail":
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

        # hitrate=0は「必中」を表す既存の規約と衝突しないよう、下限を1にクランプする
        return max(1, min(100, round(effective_hitrate)))

    # move.min_hits/max_hitsから今回のヒット回数を決める
    # 2〜5回攻撃(ボーンラッシュ等)は3/8, 3/8, 1/8, 1/8という第4世代仕様の確率分布、それ以外(固定回数)はそのまま使う
    def roll_hit_count(self, move: BaseMove) -> int:
        if move.min_hits == 2 and move.max_hits == 5:
            return random.choices([2, 3, 4, 5], weights=[3, 3, 1, 1])[0]
        return random.randint(move.min_hits, move.max_hits)

    # attackerがdefenderにmoveを撃つ。命中判定→(変化技でなければ)ダメージ計算・適用の順で行い、結果を返す
    # 複数回攻撃技は命中判定を1回だけ行い、そのあと決めたヒット回数分ダメージを繰り返し与える（相手が瀕死になったら打ち切り）
    def use_move(self, attacker: Pokemon, defender: Pokemon, move: BaseMove) -> dict:
        result = {"hit": False, "damage": 0, "effectiveness": 1.0, "hit_count": 0, "charging": False, "blocked_by_protect": False}

        # 1ターン目（溜め開始）かどうか。charging_moveが同じ技を指していれば、今回は2ターン目(攻撃)
        is_releasing_charge = attacker.current_status.charging_move is move

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
        skip_charge_turn = move.id == SOLAR_BEAM_ID and self.weather == "sun"

        # パワフルハーブを持っていれば、1回だけ溜めターンを省略する（晴れのソーラービーム等、元々溜めない場合は消費しない）
        if (move.requires_charge_turn and not is_releasing_charge and not skip_charge_turn
                and attacker.held_item.try_skip_charge_turn(self, attacker)):
            skip_charge_turn = True

        if move.requires_charge_turn and not is_releasing_charge and not skip_charge_turn:
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

        # おきみやげ等は命中・失敗に関わらず、使った時点で自分が瀕死になる（第4世代仕様）
        if move.user_faints_on_use:
            attacker.current_status.current_hp = 0

        result = self._resolve_move_hit(attacker, defender, move, result)

        # じゅうでん状態は、でんき技を使った時点で消費される（威力2倍はダメージ計算で反映済み）
        if move.type == "でんき" and move.category != CATEGORY_STATUS:
            attacker.current_status.charge_turns_remaining = 0

        return result

    # use_moveのうち、命中判定以降（回避状態・まもる・命中・ダメージ・追加効果）の処理
    def _resolve_move_hit(self, attacker: Pokemon, defender: Pokemon, move: BaseMove, result: dict) -> dict:
        # 相手に向けた技かどうか（自分自身・場に向けた変化技は、相手の回避状態やまもるの影響を受けない）
        targets_opponent = self.is_move_blocked_by_protect(move, attacker)

        # 相手が回避状態（あなをほる等で溜め中）なら、命中率に関わらず必ず外れる
        if defender.current_status.is_invulnerable and targets_opponent:
            return result

        # 相手がまもる・みきりで守っていれば、命中率に関わらず技が防がれる
        if defender.current_status.is_protected and targets_opponent:
            result["blocked_by_protect"] = True
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
            ignore_ghost_immunity = defender.current_status.is_identified
            effectiveness = get_move_effectiveness(move, defender, ignore_ghost_immunity)
            hit_count = self.roll_hit_count(move)
            for _ in range(hit_count):
                if self.is_fainted(defender):
                    break

                # 半減実は効果抜群の対応タイプの技を受けたときに1回だけ発動する（複数回攻撃なら最初の1回だけ）
                defender_item = defender.held_item
                received_multiplier = defender_item.get_received_damage_multiplier(defender, move, effectiveness)

                damage = calculate_damage(
                    attacker, defender, move, self.weather, screen_active, ignore_ghost_immunity,
                    self.get_stages(attacker), self.get_stages(defender), received_multiplier,
                )
                if received_multiplier != 1.0 and damage > 0:
                    defender_item.on_received_damage_reduced(self, defender)

                damage = self.apply_survival_effects(defender, damage)

                self.apply_damage(defender, damage)
                total_damage += damage
                result["hit_count"] += 1

            result["damage"] = total_damage
            result["effectiveness"] = effectiveness

            # テクスチャー2が参照できるよう、受けた技のタイプを記録しておく
            if result["hit_count"] > 0:
                defender.current_status.last_hit_by_type = move.type

            # かいがらのすず・いのちのたま・おうじゃのしるし等、ダメージを与えた後に発動する持ち物
            # (とんぼがえりで交代する前に発動させるため、追加効果より先に処理する)
            if total_damage > 0:
                self.apply_after_damage_items(attacker, defender, move, total_damage)

        # 命中していれば、技固有の追加効果を発動させる（無い技はBaseMoveのデフォルトで何もしない）
        move.apply_effect(self, attacker, defender, total_damage)

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
    def try_apply_stat_change(self, target, stat_name, stage_amount, chance):
        if random.random() < chance:
            self.change_stage(target, stat_name, stage_amount)
            return True
        return False

    # みやぶるでtargetを「見破った」状態にする。以後、相手の回避ランクを無視して命中判定し、
    # ノーマル/かくとう技に対するゴーストタイプの無効化も無視する（対象が場を退くと解除）
    def perform_identify(self, target):
        target.current_status.is_identified = True

    # moveがまもる・みきりで防がれる対象かどうかを判定する
    # ダメージを与える技は常に防がれる。変化技は「相手(target)」に向けた効果を持つものだけ防がれ、
    # 自分自身への効果（つるぎのまい等）や天候・設置技・壁など場に対する効果は本編仕様通り防がれない
    # のろいはゴーストタイプが使った場合だけ相手に向けた技になるため、使用者(attacker)も見て判定する
    def is_move_blocked_by_protect(self, move: BaseMove, attacker: Pokemon = None) -> bool:
        if move.category != CATEGORY_STATUS:
            return True
        for effect in move.effects:
            kind = effect[0]
            if kind in ("status", "status_random", "stat", "stat_multi", "flinch") and effect[1] == "target":
                return True
            # いたみわけ・いえきは相手のHP・特性を直接書き換えるので、相手に向けた効果として防がれる
            if kind in ("pain_split", "suppress_ability"):
                return True
            if kind == "curse" and attacker is not None and self.is_ghost_type(attacker):
                return True
        return False

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
    def try_apply_stat_multi_change(self, target, stat_changes, chance):
        if random.random() < chance:
            for stat_name, stage_amount in stat_changes:
                self.change_stage(target, stat_name, stage_amount)
            return True
        return False

    # chanceの確率でtargetに状態異常を付与する（既に何か状態異常が付いている場合は上書きしない）
    # ねむり・こんらんは残りターン数もあわせて設定する
    # こんらんだけはstatus_conditionとは別枠で管理し、他の状態異常と重複できる（既にこんらん中なら上書きしない）
    def try_apply_status(self, target, condition, chance):
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
    # おおきなねっこを持っていれば回復量が1.3倍になる
    def apply_drain(self, attacker, damage, ratio):
        heal_amount = int(damage * ratio)
        heal_amount = int(heal_amount * attacker.held_item.get_drain_multiplier())
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
    # 注意: はきだす・のみこむは未実装のため、たくわえた分のランクを解除する処理もまだ無い
    def perform_stockpile(self, attacker: Pokemon):
        if attacker.current_status.stockpile_count >= STOCKPILE_MAX:
            return
        attacker.current_status.stockpile_count += 1
        self.try_apply_stat_multi_change(attacker, [("defense", 1), ("spdef", 1)], 1.0)

    # いえき: targetの特性を消す（交代するまで）
    # 注意: 特性の効果自体がまだ実装されていないため、今は状態を記録するだけで対戦結果には影響しない
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
        attacker.ability = target.ability

        attacker.status = PokemonStatus(
            hp=attacker.status.hp,  # HPは変身前のまま変わらない
            atk=target.status.atk,
            defense=target.status.defense,
            spatk=target.status.spatk,
            spdef=target.status.spdef,
            spd=target.status.spd,
        )

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

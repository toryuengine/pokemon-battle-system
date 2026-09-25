import random

from readpokemondata import load_move_data

# move.jsonのcategoryの数値表現（物理=0, 特殊=1, 変化=2）
CATEGORY_PHYSICAL = 0
CATEGORY_SPECIAL = 1
CATEGORY_STATUS = 2


class BaseMove:
    def __init__(self, id: int):
        data = load_move_data()[str(id)]

        self.id = id
        self.name = data["name"]
        self.type = data["type"]
        self.category = data["category"]
        self.power = data["power"]
        self.pp = data["pp"]
        self.hitrate = data["hitrate"]

        self._init_extra_defaults()

    # move.jsonから読めない、技ごとの追加性質のデフォルト値をまとめて設定する。
    # move.jsonに存在しない特殊技（わるあがき等）は__init__を通さずここだけ呼び出して使う。
    # 新しい性質を追加するときはここに1箇所書けば、通常の技にも特殊技にも自動的に反映される。
    def _init_extra_defaults(self):
        # 現在の残りPP。使うたびにBattle側で1減らす
        self.current_pp = self.pp

        # 急所に当たりやすい技（きりさく等）はサブクラス側でTrueに上書きする
        self.high_crit = False

        # 優先度。通常技は0、でんこうせっか等の先制技はサブクラス側で正の値に、
        # ほえる等の後攻技は負の値に上書きする
        self.priority = 0

        # タイプを持たない技（わるあがき等）。タイプ相性を一切無視し常に等倍になる
        self.is_typeless = False

        # 一撃必殺技（じわれ等）はサブクラス側でTrueに上書きする
        self.is_ohko = False

        # 自分の残りHP割合によって威力が変わる技（じたばた等）はサブクラス側でTrueに上書きする
        self.has_hp_based_power = False

        # 1回の使用で何回ヒットするか。通常技は1〜1（1回のみ）
        # 固定2回攻撃（にどげり等）はmin_hits=max_hits=2、2〜5回攻撃（ボーンラッシュ等）はmin_hits=2, max_hits=5
        self.min_hits = 1
        self.max_hits = 1

        # 使うと次のターン反動で行動不能になる技（はかいこうせん等）はサブクラス側でTrueに上書きする
        self.requires_recharge = False

        # 1ターン目に溜めて2ターン目に攻撃する技（ソーラービーム等）はサブクラス側でTrueに上書きする
        self.requires_charge_turn = False
        # 溜めている間、相手の技を回避できる技（あなをほる・そらをとぶ等）はサブクラス側でTrueに上書きする
        self.charge_is_invulnerable = False

        # 使った時点で（命中・失敗に関わらず）自分が瀕死になる技（おきみやげ等）はサブクラス側でTrueに上書きする
        self.user_faints_on_use = False

        # ねむり状態でも使える技（ねごと）はサブクラス側でTrueに上書きする
        self.usable_while_asleep = False

        # 自分の他の技をランダムに1つ呼び出して使う技（ねごと）はサブクラス側でTrueに上書きする
        self.calls_own_random_move = False
        # ねごとで呼び出せない技（ねごと自身・きあいパンチ等）はサブクラス側でTrueに上書きする（溜め技は自動的に除外する）
        self.cannot_be_called_by_sleep_talk = False

        # 使ったターンにはダメージを与えず、2ターン後のターン終了時に攻撃する技（みらいよち）はサブクラス側でTrueに上書きする
        self.is_delayed_attack = False

        # まもる・みきりで防がれない、相手に向けた技（ほえる等）はサブクラス側でTrueに上書きする
        self.bypasses_protect = False

        # 溜め中で回避状態の相手にも当たる場合の、相手が溜めている技のID（じしん→あなをほる等）。
        # 当たった場合は威力が2倍になる。サブクラス側で上書きする
        self.hits_during_charge_move_ids = ()

        # 相手が手動で交代しようとしていれば、交代する前に攻撃する技（おいうち）はサブクラス側でTrueに上書きする
        self.hits_switching_target = False

        # 使った後2〜3ターン技が固定され、終わるとこんらんする技（げきりん・あばれる）はサブクラス側でTrueに上書きする
        self.is_rampage = False

        # 相手の防御を半分にして計算する技（第4世代のだいばくはつ）はサブクラス側でTrueに上書きする
        self.halves_target_defense = False
        # 場にしめりけのポケモンがいると失敗する（自分も瀕死にならない）技（だいばくはつ）はサブクラス側でTrueに上書きする
        self.is_explosive = False

        # 追加効果のデータ一覧。何もしない技は空リストのまま
        # 各要素の形式:
        #   ("status", target, condition, chance)            例: ("status", "target", "poison", 0.3)
        #   ("status_random", target, [condition, ...], chance) 複数候補からランダムに1つ付与
        #   ("stat", target, stat_name, stages, chance)       例: ("stat", "self", "spatk", -2, 1.0)
        #   ("stat_multi", target, [(stat_name, stages), ...], chance)  1回の判定で複数能力を同時に変化
        #   ("flinch", target, chance)
        #   ("recoil", ratio)   attacker(自分)が与えたダメージのratio分だけ反動を受ける
        #   ("recoil_max_hp", ratio)  attacker(自分)が最大HPのratio分だけ反動を受ける（わるあがき用）
        #   ("drain", ratio)    attacker(自分)が与えたダメージの一部を回復する
        #   ("heal", ratio)     attacker(自分)が最大HPの一定割合を回復する
        #   ("clear_stats",)    両者の能力ランクを全てリセットする（くろいきり等）
        #   ("belly_drum",)     最大HPの半分を削って攻撃ランクを最大(+6)にする（はらだいこ）
        #   ("curse",)          ゴーストタイプなら自分のHPを半分削って相手をのろい状態に、
        #                       それ以外なら自分の攻撃・防御+1、素早さ-1（のろい）
        #   ("charge",)         次のターンまで、でんき技の威力を2倍にする＋自分の特防+1（じゅうでん）
        #   ("stockpile",)      自分の防御・特防+1。最大3回まで（たくわえる）
        #   ("suppress_ability",) 相手の特性を消す（いえき）
        #   ("set_weather", weather)  天候を変える（"sun"/"rain"/"sandstorm"/"hail"）
        #   ("set_hazard", hazard_type)  相手の場に罠を設置する（"stealth_rock"/"spikes"/"toxic_spikes"）
        #   ("set_screen", screen_type)  自分の場に壁を張る（"reflect"/"light_screen"）
        #   ("mimic",)     相手が直前に使った技を自分の技としてコピーする（まねっこ）
        #   ("transform",) 相手の見た目・実数値(HP以外)・技・特性をコピーして変身する（ものまね）
        #   ("self_switch",) 攻撃後、自分から手持ちの生きている次の1体に強制的に交代する（とんぼがえり）
        #   ("type_change_resist",) 自分のタイプを、直前に受けた技のタイプを半減/無効にするタイプに変える（テクスチャー2）
        #   ("identify",)  相手を見破る。相手の回避ランクを無視し、ゴーストタイプの無効化も無視する（みやぶる）
        #   ("protect",)   このターンの間、相手の技をほぼ全て防ぐ（まもる・みきり）。連続成功で成功率が下がる
        #   ("endure",)    このターンの間、瀕死になるはずの攻撃をHP1で耐える（こらえる）。連続成功で成功率が下がる
        #   ("pain_split",) 自分と相手の残りHPを合計し、半分ずつ分け合う（いたみわけ）
        #   ("knock_off",)  相手の持ち物をはたき落とす（はたきおとす）
        #   ("bind",)       相手を2〜5ターン締め付け、毎ターン最大HPの1/16を削る（まきつく・すなじごく・うずしお）
        #   ("mean_look",)  相手を逃げられなくする（くろいまなざし）
        #   ("force_switch",) 相手を手持ちの他のポケモンに強制的に交代させる（ほえる）
        #   ("taunt",)      相手を3〜5ターン変化技が使えない状態にする（ちょうはつ）
        #   ("fling",)      投げつけた持ち物の効果を相手に与える（なげつける）
        #   ("destiny_bond",) 次の行動までに相手の攻撃で瀕死になると、相手も道連れにする（みちづれ）
        #   ("encore",)     相手が直前に使った技を4〜8ターンの間出し続けさせる（アンコール）
        #   ("disable",)    相手が直前に使った技を4〜7ターンの間使えなくする（かなしばり）
        #   ("release_stockpile",) たくわえた回数と、たくわえるで上がった防御・特防を元に戻す（はきだす）
        #   ("swallow",)    たくわえた回数に応じて回復し、たくわえた効果を解除する（のみこむ）
        #   ("magnet_rise",) 5ターンの間じめん技を受けなくなる（でんじふゆう）
        #   ("torment",)    相手が同じ技を2回続けて出せなくする（いちゃもん）
        #   ("nightmare",)  ねむっている相手を、毎ターン最大HPの1/4ずつ削る状態にする（あくむ）
        #   ("grudge",)     次の行動までに相手の攻撃で瀕死になると、その技のPPを0にする（おんねん）
        #   ("baton_pass",) 能力ランク等を引き継いで手持ちの次の1体に交代する（バトンタッチ）
        #   ("trick",)      自分と相手の持ち物を入れ替える（トリック）
        #   ("spite",)      相手が直前に使った技のPPを4減らす（うらみ）
        #   ("recycle",)    最後に消費した持ち物を取り戻す（リサイクル）
        #   ("substitute",) 最大HPの1/4を払って身代わりを作る（みがわり）
        #   ("psych_up",)   相手の能力ランクを自分にコピーする（じこあんじ）
        #   ("power_trick",) 自分の攻撃と防御の実数値を入れ替える（パワートリック）
        #   ("ingrain",)    根を張り、毎ターン最大HPの1/16を回復する。交代できなくなる（ねをはる）
        #   ("aqua_ring",)  毎ターン最大HPの1/16を回復する（アクアリング）
        #   ("leech_seed",) 相手に種を植え、毎ターン最大HPの1/8を奪って自分の場のポケモンを回復する（やどりぎのタネ）
        #   ("yawn",)       相手をねむけ状態にし、次のターンの終わりにねむらせる（あくび）
        #   ("perish_song",) 場の全員が、カウント0になったターンの終わりに瀕死になる（ほろびのうた）
        #   ("attract",)    性別が違う相手をメロメロ状態にする（メロメロ）
        #   ("trick_room",) 5ターンの間、素早さの遅い順に行動する（トリックルーム）
        #   ("acupressure",) ランダムな能力ランクを+2する（つぼをつく）
        #   ("eat_berry",)  相手のきのみを奪って食べ、その効果を自分が得る（むしくい・ついばむ）
        # target は "self"（attacker） か "target"（defender）
        self.effects = []

    # ダメージ計算に使う威力。使う状況によって威力が変わる技（なげつける・はきだす・からげんき等）はサブクラス側で上書きする
    # battleはみらいよちのように対戦の外から計算する場合にNoneになりうる
    def get_power(self, battle, attacker, defender) -> int:
        return self.power

    # 技を出す直前（回避状態・まもる・特性による無効化の判定より前）に呼ばれる。
    # 天候でタイプが変わる技（ウェザーボール）等はサブクラス側で上書きする
    def prepare_for_use(self, battle, attacker, defender):
        pass

    # 命中判定の直前に呼ばれる。技を出す条件を満たしていなければFalseを返し、技は失敗する（PPは消費済み）
    # なげつける（持ち物が無い）・はきだす/のみこむ（たくわえていない）等はサブクラス側で上書きする
    def try_execute(self, battle, attacker, defender) -> bool:
        return True

    # 命中していれば、self.effectsの内容を順番にBattleへ適用する
    # 状態異常・能力ランク・ひるみは、特性（クリアボディ・シンクロ等）の判定のため効果の発生元(attacker)も渡す
    def apply_effect(self, battle, attacker, defender, damage=0):
        # てんのめぐみ: 追加効果の発動率が上がる（確定で発動する効果は1.0のまま）
        chance_multiplier = battle.get_ability(attacker).secondary_chance_multiplier

        for effect in self.effects:
            kind = effect[0]

            if kind == "status":
                _, target_key, condition, chance = effect
                target = attacker if target_key == "self" else defender
                battle.try_apply_status(target, condition, min(1.0, chance * chance_multiplier), source=attacker)

            elif kind == "status_random":
                _, target_key, conditions, chance = effect
                target = attacker if target_key == "self" else defender
                if random.random() < min(1.0, chance * chance_multiplier):
                    battle.try_apply_status(target, random.choice(conditions), 1.0, source=attacker)

            elif kind == "stat":
                _, target_key, stat_name, stages, chance = effect
                target = attacker if target_key == "self" else defender
                battle.try_apply_stat_change(target, stat_name, stages, min(1.0, chance * chance_multiplier),
                                             source=attacker)

            elif kind == "stat_multi":
                _, target_key, stat_changes, chance = effect
                target = attacker if target_key == "self" else defender
                battle.try_apply_stat_multi_change(target, stat_changes, min(1.0, chance * chance_multiplier),
                                                   source=attacker)

            elif kind == "flinch":
                _, target_key, chance = effect
                target = attacker if target_key == "self" else defender
                battle.try_apply_flinch(target, min(1.0, chance * chance_multiplier), source=attacker)

            elif kind == "recoil":
                _, ratio = effect
                battle.apply_recoil(attacker, damage, ratio)

            elif kind == "recoil_max_hp":
                _, ratio = effect
                battle.apply_max_hp_recoil(attacker, ratio)

            elif kind == "drain":
                _, ratio = effect
                battle.apply_drain(attacker, damage, ratio, defender)

            elif kind == "heal":
                _, ratio = effect
                # こうごうせい・あさのひざし・つきのひかりは天候によって回復量が変わる
                if self.id in (13, 251, 253):
                    weather = battle.get_effective_weather()
                    if weather == "sun":
                        ratio = 2 / 3
                    elif weather in ("rain", "sandstorm", "hail"):
                        ratio = 1 / 4
                battle.apply_heal(attacker, ratio)

            elif kind == "clear_stats":
                battle.reset_all_stages()

            elif kind == "set_weather":
                _, weather = effect
                battle.set_weather(weather, attacker)

            elif kind == "set_hazard":
                _, hazard_type = effect
                battle.add_hazard(battle.get_trainer(defender), hazard_type)

            elif kind == "set_screen":
                _, screen_type = effect
                battle.set_screen(battle.get_trainer(attacker), screen_type, attacker)

            elif kind == "mimic":
                battle.perform_mimic(attacker, defender, self)

            elif kind == "transform":
                battle.perform_transform(attacker, defender)

            elif kind == "self_switch":
                battle.perform_self_switch(attacker)

            elif kind == "type_change_resist":
                battle.perform_type_change_resist(attacker)

            elif kind == "identify":
                battle.perform_identify(defender)

            elif kind == "protect":
                battle.perform_protect(attacker)

            elif kind == "endure":
                battle.perform_endure(attacker)

            elif kind == "pain_split":
                battle.perform_pain_split(attacker, defender)

            elif kind == "belly_drum":
                battle.perform_belly_drum(attacker)

            elif kind == "curse":
                battle.perform_curse(attacker, defender)

            elif kind == "charge":
                battle.perform_charge(attacker)

            elif kind == "stockpile":
                battle.perform_stockpile(attacker)

            elif kind == "suppress_ability":
                battle.perform_suppress_ability(defender)

            elif kind == "knock_off":
                battle.perform_knock_off(attacker, defender)

            elif kind == "bind":
                battle.perform_bind(attacker, defender)

            elif kind == "mean_look":
                battle.perform_mean_look(attacker, defender)

            elif kind == "force_switch":
                battle.perform_force_switch(attacker, defender)

            elif kind == "taunt":
                battle.perform_taunt(defender)

            elif kind == "fling":
                battle.apply_flung_item_effect(defender, self.flung_item, attacker)

            elif kind == "destiny_bond":
                battle.perform_destiny_bond(attacker)

            elif kind == "encore":
                battle.perform_encore(defender)

            elif kind == "disable":
                battle.perform_disable(defender)

            elif kind == "release_stockpile":
                battle.release_stockpile(attacker)

            elif kind == "swallow":
                battle.perform_swallow(attacker)

            elif kind == "magnet_rise":
                battle.perform_magnet_rise(attacker)

            elif kind == "torment":
                battle.perform_torment(defender)

            elif kind == "nightmare":
                battle.perform_nightmare(defender)

            elif kind == "grudge":
                battle.perform_grudge(attacker)

            elif kind == "baton_pass":
                battle.perform_baton_pass(attacker)

            elif kind == "trick":
                battle.perform_trick(attacker, defender)

            elif kind == "spite":
                battle.perform_spite(defender)

            elif kind == "recycle":
                battle.perform_recycle(attacker)

            elif kind == "substitute":
                battle.perform_substitute(attacker)

            elif kind == "psych_up":
                battle.perform_psych_up(attacker, defender)

            elif kind == "power_trick":
                battle.perform_power_trick(attacker)

            elif kind == "ingrain":
                battle.perform_ingrain(attacker)

            elif kind == "aqua_ring":
                battle.perform_aqua_ring(attacker)

            elif kind == "leech_seed":
                battle.perform_leech_seed(defender)

            elif kind == "yawn":
                battle.perform_yawn(attacker, defender)

            elif kind == "perish_song":
                battle.perform_perish_song(attacker, self)

            elif kind == "attract":
                battle.perform_attract(attacker, defender)

            elif kind == "trick_room":
                battle.perform_trick_room()

            elif kind == "acupressure":
                battle.perform_acupressure(attacker)

            elif kind == "eat_berry":
                battle.perform_eat_berry(attacker, defender)

    def __repr__(self):
        parts = []
        for key, value in vars(self).items():
            parts.append(f"{key}={value!r}")
        return f"{self.__class__.__name__}({', '.join(parts)})"

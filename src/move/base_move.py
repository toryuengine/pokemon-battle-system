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
        #   ("clear_stats",)    両者の能力ランクを全てリセットする（はき等）
        #   ("set_weather", weather)  天候を変える（"sun"/"rain"/"sandstorm"/"hail"）
        #   ("set_hazard", hazard_type)  相手の場に罠を設置する（"stealth_rock"/"spikes"/"toxic_spikes"）
        #   ("set_screen", screen_type)  自分の場に壁を張る（"reflect"/"light_screen"）
        #   ("mimic",)     相手が直前に使った技を自分の技としてコピーする（まねっこ）
        #   ("transform",) 相手の見た目・実数値(HP以外)・技・特性をコピーして変身する（ものまね）
        #   ("self_switch",) 攻撃後、自分から手持ちの生きている次の1体に強制的に交代する（とんぼがえり）
        # target は "self"（attacker） か "target"（defender）
        self.effects = []

    # 命中していれば、self.effectsの内容を順番にBattleへ適用する
    def apply_effect(self, battle, attacker, defender, damage=0):
        for effect in self.effects:
            kind = effect[0]

            if kind == "status":
                _, target_key, condition, chance = effect
                target = attacker if target_key == "self" else defender
                battle.try_apply_status(target, condition, chance)

            elif kind == "status_random":
                _, target_key, conditions, chance = effect
                target = attacker if target_key == "self" else defender
                if random.random() < chance:
                    battle.try_apply_status(target, random.choice(conditions), 1.0)

            elif kind == "stat":
                _, target_key, stat_name, stages, chance = effect
                target = attacker if target_key == "self" else defender
                battle.try_apply_stat_change(target, stat_name, stages, chance)

            elif kind == "stat_multi":
                _, target_key, stat_changes, chance = effect
                target = attacker if target_key == "self" else defender
                battle.try_apply_stat_multi_change(target, stat_changes, chance)

            elif kind == "flinch":
                _, target_key, chance = effect
                target = attacker if target_key == "self" else defender
                battle.try_apply_flinch(target, chance)

            elif kind == "recoil":
                _, ratio = effect
                battle.apply_recoil(attacker, damage, ratio)

            elif kind == "recoil_max_hp":
                _, ratio = effect
                battle.apply_max_hp_recoil(attacker, ratio)

            elif kind == "drain":
                _, ratio = effect
                battle.apply_drain(attacker, damage, ratio)

            elif kind == "heal":
                _, ratio = effect
                # こうごうせい・あさのひざし・つきのひかりは天候によって回復量が変わる
                if self.id in (13, 251, 253):
                    if battle.weather == "sun":
                        ratio = 2 / 3
                    elif battle.weather in ("rain", "sandstorm", "hail"):
                        ratio = 1 / 4
                battle.apply_heal(attacker, ratio)

            elif kind == "clear_stats":
                battle.reset_all_stages()

            elif kind == "set_weather":
                _, weather = effect
                battle.set_weather(weather)

            elif kind == "set_hazard":
                _, hazard_type = effect
                battle.add_hazard(battle.get_trainer(defender), hazard_type)

            elif kind == "set_screen":
                _, screen_type = effect
                battle.set_screen(battle.get_trainer(attacker), screen_type)

            elif kind == "mimic":
                battle.perform_mimic(attacker, defender, self)

            elif kind == "transform":
                battle.perform_transform(attacker, defender)

            elif kind == "self_switch":
                battle.perform_self_switch(attacker)

    def __repr__(self):
        parts = []
        for key, value in vars(self).items():
            parts.append(f"{key}={value!r}")
        return f"{self.__class__.__name__}({', '.join(parts)})"

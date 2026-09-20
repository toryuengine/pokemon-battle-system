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
        # 現在の残りPP。使うたびにBattle側で1減らす
        self.current_pp = self.pp

        # 急所に当たりやすい技（きりさく等）はサブクラス側でTrueに上書きする
        self.high_crit = False

        # 一撃必殺技（じわれ等）はサブクラス側でTrueに上書きする
        self.is_ohko = False

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
                battle.apply_heal(attacker, ratio)

            elif kind == "clear_stats":
                battle.reset_all_stages()

    def __repr__(self):
        parts = []
        for key, value in vars(self).items():
            parts.append(f"{key}={value!r}")
        return f"{self.__class__.__name__}({', '.join(parts)})"

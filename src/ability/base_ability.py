from typing import Optional

from readpokemondata import load_ability_data


# 特性の基底クラス。Battleは対戦の各場面でこのクラスのフック（メソッド・属性）を呼び出す。
# デフォルトは全て「何もしない」なので、各特性はサブクラスで必要なフックだけ上書きする。
# 特性ごとの状態（もらいびの発動済みフラグ等）はインスタンスに持たせ、on_switch_inでリセットする
class BaseAbility:
    # かたやぶりの特性を持つ相手の技を受けるときに無視される特性（ふゆう・ちくでん・クリアボディ等、受ける側で働くもの）
    is_breakable = False

    # かたやぶり: 相手の is_breakable な特性を無視して技を出す
    ignores_target_ability = False
    # ノーてんき: 場にいる間、天候の効果を無くす
    negates_weather = False
    # きもったま: ノーマル/かくとう技がゴーストタイプに当たる
    ignores_ghost_immunity = False
    # ノーガード: 自分が出す技・自分が受ける技が必ず命中する
    always_hits = False
    # カブトアーマー・シェルアーマー: 急所に当たらない
    prevents_critical_hit = False
    # いしあたま: 反動ダメージを受けない（わるあがきの反動は除く）
    prevents_recoil = False
    # せいしんりょく: ひるまない
    prevents_flinch = False
    # ヘドロえき: 吸収技で吸われると、相手が回復する代わりにダメージを受ける
    damages_drainer = False
    # プレッシャー: 自分に向けられた相手の技のPPを1多く減らす
    increases_opponent_pp_usage = False
    # ふゆう: 地面にいない扱い（じめん技・まきびし・どくびしを受けない）
    is_levitating = False
    # ねんちゃく: はたきおとす・トリックで持ち物を奪われない
    prevents_item_removal = False
    # きゅうばん: ほえるで交代させられない
    prevents_forced_switch = False
    # はやあし: まひによる素早さの低下を受けない
    ignores_paralysis_speed_drop = False
    # どんかん: メロメロ状態にならない
    prevents_infatuation = False
    # しめりけ: 場にいる間、だいばくはつが失敗する
    prevents_self_destruct = False

    # 天候ダメージを受けない天候（すながくれ: {"sandstorm"}、ゆきがくれ・アイスボディ: {"hail"}）
    weather_immunities = frozenset()
    # 急所ランクの上昇量（きょううん: 1）
    crit_stage_bonus = 0
    # 急所ダメージの倍率に掛かる補正（スナイパー: 1.5で、第4世代の急所2倍が3倍になる）
    critical_multiplier_bonus = 1.0
    # タイプ一致の倍率（てきおうりょく: 2.0）
    stab_multiplier = 1.5
    # 技の追加効果の発動率に掛かる倍率（てんのめぐみ: 2）
    secondary_chance_multiplier = 1
    # ピンチ実（チイラ・ヤタピ・カムラ）が発動するHP割合。Noneなら持ち物側の既定値（1/4）を使う（くいしんぼう: 1/2）
    pinch_berry_hp_ratio: Optional[float] = None
    # ねむりの残りターンが1回の行動判定で減る量（はやおき: 2）
    sleep_turn_decrement = 1

    def __init__(self, id: Optional[int] = None):
        # idがNoneのインスタンスは「特性なし」（いえきで消された状態）を表す
        self.id = id
        self.name = load_ability_data()[str(id)] if id is not None else "なし"

    # 場に出た時（対戦開始時・交代時）。特性ごとの状態のリセットもここで行う
    def on_switch_in(self, battle, pokemon):
        pass

    # 場を退く時（瀕死以外の交代）
    def on_switch_out(self, battle, pokemon):
        pass

    # ターン終了時（天候ダメージの後）
    def on_end_of_turn(self, battle, pokemon):
        pass

    # 行動する直前。Falseを返すとこのターンは行動できない（なまけ）
    def on_before_action(self, battle, pokemon) -> bool:
        return True

    # ひるんで行動できなかった時
    def on_flinched(self, battle, pokemon):
        pass

    # 持ち物を消費した時
    def on_item_consumed(self, battle, pokemon):
        pass

    # 相手の技が急所に当たった時（瀕死になった場合は呼ばれない）
    def on_critical_hit_received(self, battle, pokemon):
        pass

    # 状態異常（こんらん以外）になった時。sourceは状態異常にした相手（どくびし等で相手がいなければNone）
    def on_status_inflicted(self, battle, pokemon, condition, source):
        pass

    # ターン終了時のどく・やけどダメージの代わりに独自の処理をする場合はTrueを返す（ポイズンヒール・たいねつ）
    def on_residual_status(self, battle, pokemon, condition) -> bool:
        return False

    # 相手の技を受ける直前（命中判定の前）。Trueを返すと技を無効化する（ちくでん・ふゆう・がんじょう等）
    def on_try_hit(self, battle, attacker, defender, move) -> bool:
        return False

    # 状態異常（こんらん含む）にかかるかどうか
    def can_receive_status(self, battle, pokemon, condition) -> bool:
        return True

    # 相手によって、stat_nameのランクを下げられないかどうか
    def prevents_stat_drop(self, stat_name) -> bool:
        return False

    # 攻撃・特攻の実数値に掛かる倍率
    def get_attack_stat_multiplier(self, attacker, move) -> float:
        return 1.0

    # 防御・特防の実数値に掛かる倍率（技を受ける側）
    def get_defense_stat_multiplier(self, defender, move) -> float:
        return 1.0

    # 技の威力に掛かる倍率。powerは持ち物等の補正前の威力（じたばた等は残りHPから決めた値）
    def get_power_multiplier(self, attacker, move, power) -> float:
        return 1.0

    # 受ける技の威力に掛かる倍率
    def get_received_power_multiplier(self, defender, move) -> float:
        return 1.0

    # 最終ダメージに掛かる倍率
    def get_damage_multiplier(self, attacker, move, effectiveness) -> float:
        return 1.0

    # 受ける最終ダメージに掛かる倍率
    def get_received_damage_multiplier(self, defender, move, effectiveness) -> float:
        return 1.0

    # 素早さに掛かる倍率
    def get_speed_multiplier(self, battle, pokemon) -> float:
        return 1.0

    # 自分が出す技の命中率に掛かる倍率
    def get_accuracy_multiplier(self, attacker, move) -> float:
        return 1.0

    # 自分が受ける技の命中率に掛かる倍率
    def get_evasion_multiplier(self, battle, defender) -> float:
        return 1.0

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id!r}, name={self.name!r})"


# いえきで特性を消されたポケモンが持つ扱いになる「特性なし」
NO_ABILITY = BaseAbility()

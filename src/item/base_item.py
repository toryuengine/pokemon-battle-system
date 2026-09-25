from readpokemondata import load_item_data

# なげつけるで投げた時の威力（第4世代仕様）。持ち物ID（data/item.jsonのキー）→ 威力。ここに無い持ち物は10
FLING_POWERS = {
    2: 30,  # くろいヘドロ
    7: 30,  # しんぴのしずく
    8: 30,  # かいがらのすず
    9: 30,  # いのちのたま
    10: 60,  # あついいわ
    11: 30,  # ひかりのねんど
    15: 30,  # おうじゃのしるし
    24: 80,  # せんせいのツメ
    27: 80,  # するどいツメ
    28: 90,  # ねばりのかぎづめ
    29: 90,  # ふといホネ
    36: 30,  # どくどくだま
    41: 130,  # くろいてっきゅう
    44: 30,  # するどいキバ
    46: 60,  # しめったいわ
    49: 30,  # メトロノーム
    53: 40,  # つめたいいわ
}
DEFAULT_FLING_POWER = 10


# 持ち物の基底クラス。Battle・ダメージ計算は、持ち物の種類を見て分岐するのではなく、
# 各タイミングでここに定義したフック（メソッド）を呼び出す。デフォルトは全て「何もしない」なので、
# サブクラスは効果を発揮するタイミングのメソッドだけを上書きする。
# 持ち物のインスタンスはポケモン間で受け渡し（リサイクル・トリック等）できるよう状態を持たせず、
# 対戦中に変化する値はPokemon.current_status等、ポケモン側に持たせる。
class BaseItem:
    # こだわりハチマキ等、最初に出した技に固定される持ち物はサブクラス側でTrueに上書きする
    locks_move = False
    # くろいてっきゅうのように、ひこうタイプでも地面にいる扱いになる持ち物はサブクラス側でTrueに上書きする
    forces_grounded = False

    def __init__(self, id: int):
        self.id = id
        self.name = load_item_data()[str(id)]

    def __repr__(self):
        return f"{type(self).__name__}(id={self.id!r}, name={self.name!r})"

    # ---- なげつける ----

    # なげつけるで投げた時の威力
    @property
    def fling_power(self) -> int:
        return FLING_POWERS.get(self.id, DEFAULT_FLING_POWER)

    # なげつけるで投げつけられたtargetに与える効果（sourceは投げたポケモン）。デフォルトは威力分のダメージのみ
    def on_flung(self, battle, target, source):
        pass

    # ---- ダメージ計算（attacker側の持ち物） ----

    # 急所ランクの上昇量
    def get_crit_stage_bonus(self, attacker) -> int:
        return 0

    # 攻撃・特攻の実数値に掛かる倍率
    def get_attack_stat_multiplier(self, attacker, move) -> float:
        return 1.0

    # 技の威力に掛かる倍率
    def get_power_multiplier(self, attacker, move) -> float:
        return 1.0

    # 最終ダメージに掛かる倍率
    def get_damage_multiplier(self, attacker, effectiveness: float) -> float:
        return 1.0

    # ---- ダメージ計算（defender側の持ち物） ----

    # 受けるダメージに掛かる倍率（半減実）
    def get_received_damage_multiplier(self, defender, move, effectiveness: float) -> float:
        return 1.0

    # get_received_damage_multiplierでダメージが軽減された後に呼ばれる（半減実を消費する）
    def on_received_damage_reduced(self, battle, defender):
        pass

    # 瀕死になる攻撃ダメージをHP1で耐えるならTrueを返す（こらえるが優先される）
    def try_endure_fatal_hit(self, battle, defender) -> bool:
        return False

    # ---- 攻撃後 ----

    # attackerが技でダメージを与えた後に呼ばれる（attacker自身が瀕死なら呼ばれない）
    def on_after_damage(self, battle, attacker, defender, move, total_damage: int):
        pass

    # 吸収技（ギガドレイン等）の回復量に掛かる倍率
    def get_drain_multiplier(self) -> float:
        return 1.0

    # ---- 命中 ----

    # 持ち主が使う技の命中率に掛かる倍率
    def get_accuracy_multiplier(self, attacker, defender) -> float:
        return 1.0

    # 持ち主に向けられた技の命中率に掛かる倍率
    def get_received_accuracy_multiplier(self) -> float:
        return 1.0

    # ---- 行動順 ----

    # 素早さに掛かる倍率
    def get_speed_multiplier(self) -> float:
        return 1.0

    # 同じ優先度の中で先に行動するならTrueを返す（せんせいのツメ）
    def try_move_first(self) -> bool:
        return False

    # ---- 技の使用 ----

    # 溜め技の溜めターンを省略するならTrueを返す（パワフルハーブ）
    def try_skip_charge_turn(self, battle, pokemon) -> bool:
        return False

    # ---- 場の状態 ----

    # 持ち主が起こした天候の継続ターン数
    def get_weather_duration(self, weather: str, duration: int) -> int:
        return duration

    # 持ち主が張った壁（リフレクター・ひかりのかべ）の継続ターン数
    def get_screen_duration(self, duration: int) -> int:
        return duration

    # 持ち主が使ったしめつけ系の技（まきつく等）で相手を締め付けるターン数
    def get_binding_turns(self, turns: int) -> int:
        return turns

    # ---- 状態変化への反応・ターン終了時 ----

    # HPの減少・状態異常・能力ランクの低下など、状態が変わりうるタイミングで呼ばれる（きのみ・しろいハーブ）
    def activate(self, battle, pokemon):
        pass

    # ターン終了時、天候ダメージの後に呼ばれる（たべのこし・くろいヘドロ）
    def on_end_of_turn(self, battle, pokemon):
        pass

    # ターン終了時の最後（天候・壁の経過処理の後）に呼ばれる（どくどくだま）
    def on_end_of_turn_late(self, battle, pokemon):
        pass


# 持ち物を持っていない状態を表す。持ち物のフックを呼ぶ側でNoneチェックをしなくて済むようにするためのもの
class NoItem(BaseItem):
    def __init__(self):
        self.id = None
        self.name = None


NO_ITEM = NoItem()

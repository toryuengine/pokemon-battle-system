import random
from dataclasses import dataclass, field
from typing import List, Optional

from ability.abilityfactory import create_ability
from ability.base_ability import BaseAbility
from item.base_item import NO_ITEM, BaseItem
from item.itemfactory import create_item
from move.base_move import BaseMove
from move.movefactory import create_move
from readpokemondata import load_pokemon_data


@dataclass
class PokemonStatus:
    hp: int
    atk: int
    defense: int
    spatk: int
    spdef: int
    spd: int


# 交代しても引き継がれる、対戦中に変化する状態（現在HP・状態異常など）
@dataclass
class CurrentStatus:
    current_hp: int
    status_condition: Optional[str] = None
    # ひるみはそのターン限りの一時的な状態なので、行動チェック後にBattle側でリセットする
    is_flinched: bool = False
    # はかいこうせん等を使った次のターンは反動で行動不能。行動チェック後にBattle側でリセットする
    must_recharge: bool = False
    # ソーラービーム等、溜め中の技のインスタンス。Noneなら溜めていない。次のターンに自動でこの技を撃つ
    charging_move: Optional[BaseMove] = None
    # あなをほる等、溜め中に相手の技を回避できる状態かどうか
    is_invulnerable: bool = False
    # ねむり状態の残りターン数（0になったら自然に目覚める）
    sleep_turns_remaining: int = 0
    # こんらん状態の残りターン数（0なら混乱していない）。どく・まひ等のstatus_conditionとは別枠で、
    # 他の状態異常と重複する。交代すると解除される
    confusion_turns_remaining: int = 0
    # 直前に使った技のID（まねっこがコピーする対象を判定するために使う）。まだ何も使っていなければNone
    last_move_used_id: Optional[int] = None
    # 直前に受けたダメージ技のタイプ（テクスチャー2が変化先を判定するために使う）。まだ受けていなければNone
    last_hit_by_type: Optional[str] = None
    # みやぶるで「見破られた」状態かどうか。Trueの間は相手の回避ランクを無視して命中判定し、
    # ノーマル/かくとう技に対するゴーストタイプの無効化も無視する。場を退くと解除される
    is_identified: bool = False
    # まもる・みきりで守り状態かどうか。このターンの間だけ有効で、Battle側が毎ターン開始時にリセットする
    is_protected: bool = False
    # こらえるでHP1耐え状態かどうか。このターンの間だけ有効で、Battle側が毎ターン開始時にリセットする
    is_enduring: bool = False
    # まもる・みきり・こらえるを連続成功させた回数（本編仕様で成功率が1/3ずつ下がっていくため）。
    # これら以外の技を使う、または失敗すると0に戻る。交代すると解除される
    protect_stall_counter: int = 0
    # じゅうでんの残りターン数。使ったターンの終わりと次のターンの終わりに1ずつ減り、
    # 0より大きい間はでんき技の威力が2倍になる（でんき技を使うとその時点で解除）。交代すると解除される
    charge_turns_remaining: int = 0
    # のろい（ゴーストタイプが使った場合）を受けた状態。毎ターン終了時に最大HPの1/4を失う。交代すると解除される
    is_cursed: bool = False
    # たくわえるを使った回数（最大3回）。交代すると0に戻る
    stockpile_count: int = 0
    # いえきで特性を消された状態。交代すると解除される
    is_ability_suppressed: bool = False
    # トレースで相手の特性をコピーする前の、元の特性（トレースのインスタンス）。場を退くと元に戻す
    ability_before_trace: Optional[BaseAbility] = None
    # こだわりハチマキ・こだわりメガネ・こだわりスカーフで固定された技のインスタンス。Noneなら固定されていない。
    # 交代すると解除される
    choice_locked_move: Optional[BaseMove] = None
    # 同じ技を連続で使った回数（メトロノームの威力補正に使う）。1回目は0、違う技を使うと0に戻る。交代すると解除される
    consecutive_move_count: int = 0
    # このターンに既に行動（または行動を試みた）かどうか（フォーカスレンズの判定に使う）。毎ターン開始時にリセットする
    has_moved_this_turn: bool = False
    # たくわえるで実際に上がった防御・特防のランク（はきだす・のみこむで、この分だけ元に戻す）。交代すると0に戻る
    stockpile_defense_boost: int = 0
    stockpile_spdef_boost: int = 0
    # しめつけ系の技（まきつく・すなじごく・うずしお）で締め付けられている残りターン数と、締め付けている相手。
    # 残りターンの間、毎ターン終了時に最大HPの1/16を失う。締め付けている相手が場を退くと解除される
    bound_turns_remaining: int = 0
    bound_by: Optional["Pokemon"] = None
    # くろいまなざしで逃げられなくした相手（Noneなら逃げられる）。その相手が場を退くと解除される
    trapped_by: Optional["Pokemon"] = None
    # ちょうはつの残りターン数。0より大きい間は変化技を選べない
    taunt_turns_remaining: int = 0
    # アンコールで固定された技のインスタンスと残りターン数。固定されている間はこの技しか選べない
    encore_move: Optional[BaseMove] = None
    encore_turns_remaining: int = 0
    # かなしばりで使えなくされた技のインスタンスと残りターン数
    disabled_move: Optional[BaseMove] = None
    disable_turns_remaining: int = 0
    # いちゃもんを受けた状態。同じ技を2回続けて選べない
    is_tormented: bool = False
    # あくむを受けた状態。ねむっている間、毎ターン終了時に最大HPの1/4を失う（目覚めると解除される）
    has_nightmare: bool = False
    # みちづれ・おんねんの状態。次に自分が行動しようとするまで有効
    is_destiny_bond_active: bool = False
    is_grudge_active: bool = False
    # でんじふゆうの残りターン数。0より大きい間はじめん技・まきびし・どくびしを受けない
    magnet_rise_turns_remaining: int = 0
    # みがわりの残りHP。0より大きい間は身代わりがいる。交代すると消える（バトンタッチでは引き継ぐ）
    substitute_hp: int = 0
    # パワートリックで攻撃と防御の実数値を入れ替えている状態。交代すると元に戻る（バトンタッチでは引き継ぐ）
    is_power_trick_active: bool = False
    # ねをはるで根を張った状態。毎ターン終了時に最大HPの1/16を回復し、自分の意思で交代できず、ほえるも受けない。
    # 地面にいる扱いになる。交代すると解除される（バトンタッチでは引き継ぐ）
    is_ingrained: bool = False
    # アクアリングを張った状態。毎ターン終了時に最大HPの1/16を回復する。交代すると解除される（バトンタッチでは引き継ぐ）
    has_aqua_ring: bool = False
    # やどりぎのタネを植えられた状態。毎ターン終了時に最大HPの1/8を奪われ、相手の場のポケモンが回復する。
    # 植えられた側が交代すると解除される（バトンタッチでは引き継ぐ）
    is_seeded: bool = False
    # あくびによる「ねむけ」の残りターン数（0ならねむけ無し）。使ったターンと次のターンの終わりに1ずつ減り、
    # 0になった時点でねむり状態になる。交代すると解除される（バトンタッチでも引き継がない）
    yawn_turns_remaining: int = 0
    # ほろびのうたの残りターン数（0ならかかっていない）。毎ターン終了時に1ずつ減り、0になると瀕死になる。
    # 交代すると解除される（バトンタッチでは引き継ぐ）
    perish_turns_remaining: int = 0
    # メロメロにした相手（Noneならメロメロ状態ではない）。行動するたびに1/2の確率で動けない。
    # 自分かその相手が場を退くと解除される（バトンタッチでも引き継がない）
    infatuated_by: Optional["Pokemon"] = None
    # このターンに攻撃技で自分の本体にダメージを与えた相手（Noneならこのターンはダメージを受けていない）。
    # ゆきなだれ・リベンジの威力、きあいパンチの失敗の判定に使う。毎ターン開始時にBattle側でリセットする
    # (みがわりが受けた攻撃・こんらんの自傷・ターン終了時のダメージは含まない)
    damaged_by_this_turn: Optional["Pokemon"] = None
    # 手動で交代しようとしている最中（おいうちを交代前に受ける間だけTrue）
    is_switching_out: bool = False
    # 場に出てから使った技のID（とっておきの成否判定に使う）。交代すると空に戻る（バトンタッチでも引き継がない）
    used_move_ids: set = field(default_factory=set)
    # げきりん・あばれるで固定されている技のインスタンスと、固定の残りターン数（この技を出す回数）。
    # 固定が終わるとこんらんする。行動できなかった・交代した場合は、こんらんせずに固定が解ける
    rampage_move: Optional[BaseMove] = None
    rampage_turns_remaining: int = 0


class Pokemon:
    def __init__(self, pokemon_id: int, indivisual_id: int):
        pokemon_data = load_pokemon_data()

        entry = pokemon_data[pokemon_id]
        set_data = entry["indivisual"][indivisual_id]

        self.name: str = entry["name"]
        self.type1: int = entry["type1"]
        self.type2: Optional[int] = entry["type2"]
        # 性別（"male"/"female"。Noneなら性別不明）。pokemon.jsonの個体データに"gender"があればそれを使う
        self.gender: Optional[str] = set_data.get("gender")
        # 種族が持ちうる特性の中からこの個体の特性をランダムに1つ選び、特性クラスのインスタンスとして持つ
        self.ability: BaseAbility = create_ability(random.choice(entry["ability"]))
        self.status: PokemonStatus = _parse_status(set_data["status"])
        self.current_status: CurrentStatus = CurrentStatus(current_hp=self.status.hp)
        # 持っている持ち物のインスタンス。きのみ等を使い切ると(消費すると)Noneになる
        self.item: Optional[BaseItem] = create_item(set_data["item"]) if set_data["item"] is not None else None
        # 最後に消費した持ち物（リサイクルで取り戻す対象）。まだ何も消費していなければNone
        self.consumed_item: Optional[BaseItem] = None

        self.moves: List[BaseMove] = []
        for move_id in set_data["move"]:
            self.moves.append(create_move(move_id))

    # 持ち物の効果を呼び出すときに使う。持ち物を持っていなければ効果なしのNO_ITEMを返すので、呼び出し側でNoneチェックが要らない
    @property
    def held_item(self) -> BaseItem:
        return self.item if self.item is not None else NO_ITEM

    # ひこうタイプ・ふゆうでも地面にいる扱いになるか（くろいてっきゅうを持っている、またはねをはるで根を張っている）
    @property
    def is_forced_grounded(self) -> bool:
        return self.held_item.forces_grounded or self.current_status.is_ingrained

    def __repr__(self):
        return (
            f"Pokemon(name={self.name!r}, type1={self.type1!r}, type2={self.type2!r}, "
            f"status={self.status!r}, item={self.item!r}, ability={self.ability!r}, "
            f"moves={self.moves!r})"
        )


def _parse_status(status_data) -> PokemonStatus:
    return PokemonStatus(
        hp=status_data["hp"],
        atk=status_data["atk"],
        defense=status_data["def"],
        spatk=status_data["spatk"],
        spdef=status_data["spdef"],
        spd=status_data["spd"],
    )

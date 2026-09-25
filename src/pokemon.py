import random
from dataclasses import dataclass
from typing import List, Optional

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
    # こだわりハチマキ・こだわりメガネ・こだわりスカーフで固定された技のインスタンス。Noneなら固定されていない。
    # 交代すると解除される
    choice_locked_move: Optional[BaseMove] = None
    # 同じ技を連続で使った回数（メトロノームの威力補正に使う）。1回目は0、違う技を使うと0に戻る。交代すると解除される
    consecutive_move_count: int = 0
    # このターンに既に行動（または行動を試みた）かどうか（フォーカスレンズの判定に使う）。毎ターン開始時にリセットする
    has_moved_this_turn: bool = False


class Pokemon:
    def __init__(self, pokemon_id: int, indivisual_id: int):
        pokemon_data = load_pokemon_data()

        entry = pokemon_data[pokemon_id]
        set_data = entry["indivisual"][indivisual_id]

        self.name: str = entry["name"]
        self.type1: int = entry["type1"]
        self.type2: Optional[int] = entry["type2"]
        # 種族が持ちうる特性の中からこの個体の特性をランダムに1つ選ぶ
        self.ability: int = random.choice(entry["ability"])
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

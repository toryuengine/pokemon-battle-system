"""Agent に渡す観測（Observation）。

Agent には Battle や相手の Pokemon そのものを渡さず、ここで作る観測だけを渡す（CLAUDE.md 3.3節）。
- 自分側：全部見える（セット・現在HP・PP・状態異常・能力ランク等）
- 相手側：場に出てきた個体の種族、見た目で分かるタイプ・HPの割合・状態異常・能力ランク、使った技、
  消費・はたきおとす等で判明した持ち物だけ。場に出ていない個体は数しか分からない
- 交換の時：直前の相手3体の種族だけ（技・持ち物は見られない。仕様書5節）

観測はすべて作った時点の写しで、Agent が書き換えても対戦には影響しない。
"""
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

from factory.generation import FactoryPokemon
from factory.hint import Hint

ACTION_MOVE = "move"
ACTION_SWITCH = "switch"


# ターンの行動。kindが"move"ならindexは技の位置（0〜3。わるあがきしかできないときはNone）、
# "switch"ならindexは交代先の手持ちの位置
@dataclass(frozen=True)
class TurnAction:
    kind: str
    index: Optional[int]

    @staticmethod
    def move(slot: Optional[int]) -> "TurnAction":
        return TurnAction(ACTION_MOVE, slot)

    @staticmethod
    def switch(party_index: int) -> "TurnAction":
        return TurnAction(ACTION_SWITCH, party_index)


# どの判断でも見てよい、挑戦の進み具合
# battle_numberは連勝の何戦目か（1始まり。21・49ならネジキ戦）。レンタルの時点では次の対戦の番号
@dataclass(frozen=True)
class FactoryContext:
    round_number: int
    battle_in_round: int
    win_streak: int
    battle_number: int
    rent_trade_count: int
    is_nejiki: bool


# レンタル：候補6体の詳細（セット・個体値・性別・特性が全部分かる）から3体を選ぶ
@dataclass(frozen=True)
class RentalObservation:
    context: FactoryContext
    candidates: Tuple[FactoryPokemon, ...]


# 並び順：自分の3体と、対戦前ヒントから、先発・並び順を決める
@dataclass(frozen=True)
class OrderObservation:
    context: FactoryContext
    team: Tuple[FactoryPokemon, ...]
    hint: Hint


# 交換：自分の3体と、直前の相手3体の種族ID（相手の技・持ち物は見られない）
@dataclass(frozen=True)
class TradeObservation:
    context: FactoryContext
    team: Tuple[FactoryPokemon, ...]
    opponent_pokemon_ids: Tuple[int, ...]


@dataclass(frozen=True)
class MoveView:
    slot: int
    move_id: int
    current_pp: int
    max_pp: int


# 自分の手持ちの1体の、対戦中の状態
@dataclass(frozen=True)
class OwnPokemonView:
    party_index: int
    pokemon: FactoryPokemon
    current_hp: int
    max_hp: int
    status_condition: Optional[str]
    # 今の持ち物・特性・技（消費・トリック・トレース・ものまね等で変わる）
    item_id: Optional[int]
    ability_id: int
    moves: Tuple[MoveView, ...]
    # 実数値（"hp"/"atk"/"defense"/"spatk"/"spdef"/"spd"）
    stats: Dict[str, int]
    is_active: bool

    @property
    def is_fainted(self) -> bool:
        return self.current_hp <= 0


# 相手の1体のうち、場に出てきて見えた情報
@dataclass(frozen=True)
class OpponentPokemonView:
    party_index: int
    pokemon_id: int
    # 見た目で分かるタイプ（data/type.jsonのID）
    types: Tuple[int, Optional[int]]
    # HPの割合（0〜1。本編のHPバー相当）
    hp_ratio: float
    status_condition: Optional[str]
    # 使ったのを見た技のID（使った順、重複なし）
    revealed_move_ids: Tuple[int, ...]
    # 消費・はたきおとす・トリック等で判明した、元の持ち物のID（分かっていなければNone）
    revealed_item_id: Optional[int]
    is_active: bool

    @property
    def is_fainted(self) -> bool:
        return self.hp_ratio <= 0


# 場の片側の状態（壁・設置技等。どちらの側も見えている）
@dataclass(frozen=True)
class SideConditions:
    reflect_turns: int
    light_screen_turns: int
    safeguard_turns: int
    stealth_rock: bool
    spikes: int
    toxic_spikes: int


# 毎ターンの行動・瀕死時の交代先を決めるときの観測
@dataclass(frozen=True)
class TurnObservation:
    context: FactoryContext
    hint: Optional[Hint]
    turn: int
    own_team: Tuple[OwnPokemonView, ...]
    own_active_index: int
    # 場に出ている個体の能力ランク（"atk"/"defense"/"spatk"/"spdef"/"spd"/"accuracy"/"evasion"）
    own_stages: Dict[str, int]
    # 相手の手持ちの数と、そのうち場に出てきて見えた個体（party_indexの順）
    opponent_team_size: int
    opponent_seen: Tuple[OpponentPokemonView, ...]
    opponent_active_index: int
    opponent_stages: Dict[str, int]
    # 場に出ている個体の、見て分かる一時的な状態（"confused"・"substitute"・"seeded"等。下のVOLATILE_FLAGS）
    own_volatile: Tuple[str, ...]
    opponent_volatile: Tuple[str, ...]
    own_side: SideConditions
    opponent_side: SideConditions
    weather: Optional[str]
    trick_room_turns: int
    # 今選べる行動。ターンの行動ならこの中から1つ返す。瀕死時等の交代先選びでは交代だけが並ぶ
    legal_actions: Tuple[TurnAction, ...] = field(default_factory=tuple)

    @property
    def own_active(self) -> OwnPokemonView:
        return self.own_team[self.own_active_index]

    @property
    def opponent_active(self) -> Optional[OpponentPokemonView]:
        for pokemon in self.opponent_seen:
            if pokemon.party_index == self.opponent_active_index:
                return pokemon
        return None

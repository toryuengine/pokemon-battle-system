# 判断する主体（Agent）に渡す観測。プレイヤーが知り得る情報だけを入れ、Battleや相手のPokemonそのものは渡さない
# （CLAUDE.md 3.3節）。自分のポケモンは全部見えるが、相手のポケモンは見た目と対戦中に判明したことだけが見える
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from factory.hints import Hint
from readpokemondata import load_move_data, load_type_data

CATEGORY_NAMES = {0: "物理", 1: "特殊", 2: "変化"}


@dataclass(frozen=True)
class MoveView:
    id: int
    name: str
    type: str
    category: str
    power: int
    hitrate: int
    pp: int
    current_pp: int


# 自分のポケモン（レンタル候補・自分のチーム）。技・持ち物・特性・実数値まで全部見える
@dataclass(frozen=True)
class OwnPokemonView:
    name: str
    types: Tuple[str, ...]
    level: int
    iv: int
    nature: str
    ability: str
    item: Optional[str]
    stats: Dict[str, int]
    current_hp: int
    status_condition: Optional[str]
    moves: Tuple[MoveView, ...]

    @property
    def is_fainted(self) -> bool:
        return self.current_hp <= 0


# 相手のポケモン。見た目で分かる種族・タイプ・レベルと、HPの割合・状態異常、対戦中に使われて判明した技だけが見える
# 持ち物・特性は、発動して判明したものを記録する仕組みがまだ無いので、今は見えない
@dataclass(frozen=True)
class OpponentPokemonView:
    name: str
    types: Tuple[str, ...]
    level: int
    hp_ratio: float
    status_condition: Optional[str]
    revealed_moves: Tuple[str, ...]

    @property
    def is_fainted(self) -> bool:
        return self.hp_ratio <= 0


# 種族だけが分かる相手のポケモン（5節: 交換のときは技・持ち物を確認できない）
@dataclass(frozen=True)
class SpeciesView:
    name: str
    types: Tuple[str, ...]


# 周・連勝の状況
@dataclass(frozen=True)
class FactoryContext:
    level: str
    win_streak: int
    round_number: int
    battle_in_round: int
    rent_trade_count: int


@dataclass(frozen=True)
class RentalObservation:
    context: FactoryContext
    candidates: Tuple[OwnPokemonView, ...]


@dataclass(frozen=True)
class OrderObservation:
    context: FactoryContext
    team: Tuple[OwnPokemonView, ...]
    hint: Optional[Hint]  # ネジキ戦はヒントが無いのでNone
    is_brain_battle: bool


@dataclass(frozen=True)
class TradeObservation:
    context: FactoryContext
    team: Tuple[OwnPokemonView, ...]
    opponents: Tuple[SpeciesView, ...]


# 対戦中の1ターンの判断に使う観測
@dataclass(frozen=True)
class TurnObservation:
    context: FactoryContext
    turn: int
    active_index: int                       # team の中で場に出ている個体のインデックス
    team: Tuple[OwnPokemonView, ...]
    stat_stages: Dict[str, int]             # 自分の場のポケモンの能力ランク
    opponent_active: OpponentPokemonView
    opponent_stat_stages: Dict[str, int]
    opponent_seen: Tuple[OpponentPokemonView, ...]  # これまでに場に出てきた相手のポケモン
    opponent_remaining: int                 # 相手の手持ちのうち瀕死でない数（ボールの表示で分かる）
    weather: Optional[str]
    move_options: Tuple[MoveView, ...]      # このターン選べる技（固定されていれば1つだけ）
    switch_options: Tuple[int, ...]         # このターン交代先に選べる team のインデックス（交代できなければ空）


# 瀕死・とんぼがえり等で交代先を選ぶときの観測
@dataclass(frozen=True)
class ReplacementObservation:
    context: FactoryContext
    team: Tuple[OwnPokemonView, ...]
    opponent_active: OpponentPokemonView
    switch_options: Tuple[int, ...]


def type_names(type1: int, type2: Optional[int]) -> Tuple[str, ...]:
    names = load_type_data()
    return tuple(names[str(type_id)] for type_id in (type1, type2) if type_id is not None)


def move_view(move) -> MoveView:
    # わるあがき等、move.jsonに無い技はインスタンスの値をそのまま使う
    data = load_move_data().get(str(move.id), {})
    return MoveView(id=move.id, name=move.name, type=move.type, category=CATEGORY_NAMES.get(move.category, "?"),
                    power=move.power, hitrate=move.hitrate, pp=data.get("pp", move.pp), current_pp=move.current_pp)


def own_view(pokemon) -> OwnPokemonView:
    status = pokemon.status
    return OwnPokemonView(
        name=pokemon.name,
        types=type_names(pokemon.type1, pokemon.type2),
        level=pokemon.level,
        iv=pokemon.iv,
        nature=pokemon.nature,
        ability=pokemon.ability.name,
        item=pokemon.item.name if pokemon.item is not None else None,
        stats={"hp": status.hp, "atk": status.atk, "def": status.defense, "spatk": status.spatk,
               "spdef": status.spdef, "spd": status.spd},
        current_hp=pokemon.current_status.current_hp,
        status_condition=pokemon.current_status.status_condition,
        moves=tuple(move_view(move) for move in pokemon.moves),
    )


def opponent_view(pokemon) -> OpponentPokemonView:
    move_names = load_move_data()
    return OpponentPokemonView(
        name=pokemon.name,
        types=type_names(pokemon.type1, pokemon.type2),
        level=pokemon.level,
        hp_ratio=max(0, pokemon.current_status.current_hp) / pokemon.status.hp,
        status_condition=pokemon.current_status.status_condition,
        # 判明した順は持っていないので、技構成の並び順で返す
        revealed_moves=tuple(move_names[str(move.id)]["name"] for move in pokemon.moves
                             if move.id in pokemon.revealed_move_ids),
    )


def species_view(pokemon) -> SpeciesView:
    return SpeciesView(name=pokemon.name, types=type_names(pokemon.type1, pokemon.type2))


def stages_dict(stages) -> Dict[str, int]:
    return {key: getattr(stages, key) for key in ("atk", "defense", "spatk", "spdef", "spd", "accuracy", "evasion")}

"""対戦前ヒント（仕様書7節・シングル）。"""
from collections import Counter
from dataclasses import dataclass
from typing import Optional, Sequence, Tuple

from factory import rules
from factory.generation import FactoryPokemon
from readpokemondata import load_type_data


# 科学者が教えてくれる相手の情報。kindによって埋まる項目が違う（教えてくれない項目はNone）
#   all_names          pokemon_ids に3体の種族ID（先発から順）
#   first_two_names    pokemon_ids に先頭から2体の種族ID
#   lead_name_and_move pokemon_ids に先発の種族ID、move_id に先発の1番目の技
#   lead_move          move_id に先発の1番目の技
#   most_common_type   type_id に3体で最も多いタイプ（data/type.jsonのID）
@dataclass(frozen=True)
class Hint:
    kind: str
    pokemon_ids: Optional[Tuple[int, ...]] = None
    move_id: Optional[int] = None
    type_id: Optional[int] = None


# data/type.json のID → 第4世代の内部番号の順（小さいほど同数のときに優先）
def _type_priority() -> dict:
    priority_by_name = {name: index for index, name in enumerate(rules.TYPE_PRIORITY_NAMES)}
    return {int(type_id): priority_by_name[name] for type_id, name in load_type_data().items()}


# 3体のタイプ（複合タイプは両方を1つずつ数える）で最も多いタイプ。同数なら内部番号の小さい方
def most_common_type(team: Sequence[FactoryPokemon]) -> int:
    counts = Counter(type_id for pokemon in team for type_id in pokemon.types if type_id is not None)
    priority = _type_priority()
    return min(counts, key=lambda type_id: (-counts[type_id], priority[type_id]))


# 周の番号と相手のチーム（先発から順）から、対戦前ヒントを作る
def make_hint(round_number: int, opponent_team: Sequence[FactoryPokemon]) -> Hint:
    kind = rules.hint_kind(round_number)
    lead = opponent_team[0]
    if kind == rules.HINT_ALL_NAMES:
        return Hint(kind, pokemon_ids=tuple(pokemon.pokemon_id for pokemon in opponent_team))
    if kind == rules.HINT_FIRST_TWO_NAMES:
        return Hint(kind, pokemon_ids=tuple(pokemon.pokemon_id for pokemon in opponent_team[:2]))
    if kind == rules.HINT_LEAD_NAME_AND_MOVE:
        return Hint(kind, pokemon_ids=(lead.pokemon_id,), move_id=lead.move_ids[0])
    if kind == rules.HINT_LEAD_MOVE:
        return Hint(kind, move_id=lead.move_ids[0])
    return Hint(kind, type_id=most_common_type(opponent_team))

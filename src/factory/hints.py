# 7節 対戦前ヒント（シングル）。周が進むほど教えてもらえる情報が減る
from dataclasses import dataclass
from typing import List, Optional, Tuple

from factory import rules
from factory.generator import FactoryMon
from readpokemondata import load_move_data, load_type_data


@dataclass(frozen=True)
class Hint:
    kind: str                       # rules.HINT_* のどれか
    names: Tuple[str, ...] = ()     # 教えてもらえたポケモンの名前（先頭が先発）
    lead_move: Optional[str] = None  # 先発の1番目の技の名前
    most_common_type: Optional[str] = None  # 3体で最も多いタイプの名前

    def describe(self) -> str:
        if self.kind == rules.HINT_ALL_NAMES:
            return f"相手は {'・'.join(self.names)} を使ってくる"
        if self.kind == rules.HINT_TWO_NAMES:
            return f"相手は {'・'.join(self.names)} の順で出してくる"
        if self.kind == rules.HINT_LEAD_AND_MOVE:
            return f"先発は {self.names[0]} で、{self.lead_move} を覚えている"
        if self.kind == rules.HINT_LEAD_MOVE:
            return f"先発は {self.lead_move} を覚えている"
        return f"相手は {self.most_common_type}タイプ が多い"


def make_hint(round_number: int, opponent_team: List[FactoryMon]) -> Hint:
    kind = rules.hint_kind(round_number)
    lead = opponent_team[0].template
    if kind == rules.HINT_ALL_NAMES:
        return Hint(kind=kind, names=tuple(mon.name for mon in opponent_team))
    if kind == rules.HINT_TWO_NAMES:
        return Hint(kind=kind, names=tuple(mon.name for mon in opponent_team[:2]))
    # 「1番目の技」は技選択画面で左上にある技＝セットの技の並びの先頭
    lead_move = load_move_data()[str(lead.moves[0].id)]["name"]
    if kind == rules.HINT_LEAD_AND_MOVE:
        return Hint(kind=kind, names=(lead.name,), lead_move=lead_move)
    if kind == rules.HINT_LEAD_MOVE:
        return Hint(kind=kind, lead_move=lead_move)
    return Hint(kind=kind, most_common_type=most_common_type(opponent_team))


# 3体のタイプ（2タイプなら両方）を数え、最も多いタイプの名前を返す。同数ならTYPE_TIEBREAK_ORDERの先の方
def most_common_type(team: List[FactoryMon]) -> str:
    type_names = load_type_data()
    counts = {}
    for mon in team:
        for type_id in (mon.template.type1, mon.template.type2):
            if type_id is None:
                continue
            name = type_names[str(type_id)]
            counts[name] = counts.get(name, 0) + 1
    return min(counts, key=lambda name: (-counts[name], rules.TYPE_TIEBREAK_ORDER.index(name)))

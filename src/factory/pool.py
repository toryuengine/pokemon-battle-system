# ファクトリーで使うポケモンのセット（種族＋技4つ＋持ち物＋性格＋努力値）の一覧と、周ごとの絞り込み
from dataclasses import dataclass
from typing import List, Optional

from factory.rules import GROUP1_FALLBACK_VARIATIONS, PoolSpec
from readpokemondata import load_pokemon_data


# data/pokemon.json の1セットを指す参照。対戦用のPokemonはここからレベル・個体値を決めて作る
@dataclass(frozen=True)
class SetRef:
    pokemon_id: int      # data/pokemon.json の種族のインデックス
    indivisual_id: int   # その種族の何番目のセットか
    name: str
    dex_no: int
    item: Optional[int]
    group: int
    variation: int
    legendary: bool


class SetPool:
    def __init__(self, sets: Optional[List[SetRef]] = None):
        self.sets: List[SetRef] = sets if sets is not None else _load_all_sets()

    # PoolSpecに当てはまるセットの一覧。グループ1のセットが1つも無ければ（データ未整備）、
    # round_numberに応じたグループ2のバリエーションで代用する
    def select(self, spec: PoolSpec, round_number: Optional[int] = None) -> List[SetRef]:
        selected = [s for s in self.sets if _matches(s, spec)]
        if not selected and spec.group == 1:
            variations = GROUP1_FALLBACK_VARIATIONS.get(round_number, (1,))
            fallback = PoolSpec(group=2, variations=variations, legendary=False)
            selected = [s for s in self.sets if _matches(s, fallback)]
        return selected


def _matches(set_ref: SetRef, spec: PoolSpec) -> bool:
    if set_ref.group != spec.group:
        return False
    if set_ref.legendary:
        # 伝説のポケモンは、使ってよい周ならバリエーションを問わない（8節の49戦目と同じ扱い）
        return spec.legendary
    return spec.variations is None or set_ref.variation in spec.variations


def _load_all_sets() -> List[SetRef]:
    sets = []
    for pokemon_id, entry in enumerate(load_pokemon_data()):
        for indivisual_id, set_data in enumerate(entry["indivisual"]):
            sets.append(SetRef(
                pokemon_id=pokemon_id,
                indivisual_id=indivisual_id,
                name=entry["name"],
                dex_no=entry["dex_no"],
                item=set_data["item"],
                group=set_data["group"],
                variation=set_data["variation"],
                legendary=entry.get("legendary", False),
            ))
    return sets

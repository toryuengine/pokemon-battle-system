"""ファクトリーのポケモン生成（レンタル候補・相手のチーム）。

ポケモンは「どのセットか・レベル・個体値・性別・特性」だけを FactoryPokemon に持ち、対戦のたびに
build() で Pokemon を作り直す。勝利後の全回復（HP・PP・状態異常・消費した持ち物・ものまねで覚えた技等が元に戻る）は、
作り直すことで行う。
"""
import random
from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, Tuple

from factory import rules
from pokemon import Pokemon, _roll_gender
from readpokemondata import load_nejiki_pool, load_pokemon_data, load_round_pool


# ファクトリーの1体。対戦ごとに build() で Pokemon を作る
# source_roundは、どの周の構成・個体値で作ったか（ネジキ戦のポケモンは"silver"/"gold"）。表示・分析用
@dataclass(frozen=True)
class FactoryPokemon:
    pokemon_id: int
    indivisual_id: int
    level: int
    iv: int
    gender: Optional[str]
    ability_id: int
    source_round: object = None

    def build(self) -> Pokemon:
        return Pokemon(self.pokemon_id, self.indivisual_id, level=self.level, iv=self.iv,
                       gender=self.gender, ability_id=self.ability_id)

    @property
    def _entry(self) -> dict:
        return load_pokemon_data()[self.pokemon_id]

    @property
    def _set_data(self) -> dict:
        return self._entry["indivisual"][self.indivisual_id]

    @property
    def name(self) -> str:
        return self._entry["name"]

    @property
    def item_id(self) -> Optional[int]:
        return self._set_data["item"]

    @property
    def move_ids(self) -> List[int]:
        return list(self._set_data["move"])

    @property
    def types(self) -> Tuple[int, Optional[int]]:
        return self._entry["type1"], self._entry["type2"]

    @property
    def is_legendary(self) -> bool:
        return self._entry["legendary"]


# セット（pokemon_id, indivisual_id）から、性別・特性を乱数で決めて FactoryPokemon を作る
def make_factory_pokemon(pokemon_id: int, indivisual_id: int, iv: int, rng: random.Random,
                         level: int = rules.OPEN_LEVEL, source_round=None) -> FactoryPokemon:
    entry = load_pokemon_data()[pokemon_id]
    set_data = entry["indivisual"][indivisual_id]
    gender = set_data["gender"] if "gender" in set_data else _roll_gender(entry.get("female_rate"), rng)
    ability_id = rng.choice(entry["ability"])
    return FactoryPokemon(pokemon_id, indivisual_id, level, iv, gender, ability_id, source_round)


# 周の番号 → その周で出てくるセットの一覧
def round_pool(round_number: int) -> List[Tuple[int, int]]:
    return load_round_pool(rules.round_pool_index(round_number))


# poolから、種族も持ち物もused_species・used_itemsと重ならないセットを1つ選ぶ（種族クローズ・アイテムクローズ）
def _pick_set(pool: Sequence[Tuple[int, int]], used_species: set, used_items: set,
              rng: random.Random) -> Tuple[int, int]:
    entries = load_pokemon_data()
    candidates = [(pokemon_id, indivisual_id) for pokemon_id, indivisual_id in pool
                  if pokemon_id not in used_species
                  and entries[pokemon_id]["indivisual"][indivisual_id]["item"] not in used_items]
    if not candidates:
        raise RuntimeError("種族・持ち物が重ならないセットが残っていません")
    return rng.choice(candidates)


# (周の番号 or ネジキの種類, プール, 個体値) の並びから、1体ずつ種族・持ち物が重ならないように選んで作る
# 持ち物を持たないセット（item=None）は、持ち物の重なりを見ない
def _pick_team(slots: Iterable[Tuple[object, Sequence[Tuple[int, int]], int]], rng: random.Random,
               excluded_species: Iterable[int] = (), excluded_items: Iterable[int] = ()) -> List[FactoryPokemon]:
    used_species = set(excluded_species)
    used_items = {item for item in excluded_items if item is not None}
    team = []
    for source_round, pool, iv in slots:
        pokemon_id, indivisual_id = _pick_set(pool, used_species, used_items, rng)
        pokemon = make_factory_pokemon(pokemon_id, indivisual_id, iv, rng, source_round=source_round)
        team.append(pokemon)
        used_species.add(pokemon_id)
        if pokemon.item_id is not None:
            used_items.add(pokemon.item_id)
    return team


# 4・6.3 レンタル候補6体。全員が別種族・別の持ち物。
# 「強いポケモン」（rules.strong_rental_count）の分は次の周の構成・個体値で作る。
# 強いポケモンが候補のどこに来るかは分からないので、作った後で並びを混ぜる（推測。READMEの「推測で決めた細かい仕様」）
def generate_rental_candidates(round_number: int, rent_trade_count: int, rng: random.Random) -> List[FactoryPokemon]:
    strong_count = rules.strong_rental_count(rent_trade_count)
    strong_slot = (round_number + 1, round_pool(round_number + 1), rules.iv_for_round(round_number + 1))
    normal_slot = (round_number, round_pool(round_number), rules.iv_for_round(round_number))
    slots = [strong_slot] * strong_count + [normal_slot] * (rules.RENTAL_CANDIDATE_COUNT - strong_count)
    candidates = _pick_team(slots, rng)
    rng.shuffle(candidates)
    return candidates


# 5・6.4・8 相手のチーム3体。プレイヤーの手持ちと同じ種族・同じ持ち物は除外し、チームの中でも種族・持ち物は重ならない。
# battle_numberは連勝の何戦目か（1始まり）。21戦目・49戦目はネジキのプールと個体値で作る。
# 第1〜6戦で「今の周か1つ前の周」のどちらを使うかは、チーム単位で半々に決める（推測。READMEの「推測で決めた細かい仕様」）
def generate_opponent_team(round_number: int, battle_in_round: int, battle_number: int,
                           player_team: Sequence[FactoryPokemon], rng: random.Random) -> List[FactoryPokemon]:
    kind = rules.nejiki_kind(battle_number)
    if kind is not None:
        slot = (kind, load_nejiki_pool(kind), rules.NEJIKI_IV[kind])
    else:
        source_round = rng.choice(rules.opponent_round_candidates(round_number, battle_in_round))
        slot = (source_round, round_pool(source_round), rules.iv_for_round(source_round))
    return _pick_team([slot] * rules.TEAM_SIZE, rng,
                      excluded_species=[pokemon.pokemon_id for pokemon in player_team],
                      excluded_items=[pokemon.item_id for pokemon in player_team])

# レンタル候補・対戦相手のチームの生成（4節・5節・6節・8節）
import copy
import random
from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Set

from factory import rules
from factory.pool import SetPool, SetRef
from pokemon import Pokemon


# ファクトリーで使う1体。セット・レベル・個体値と、生成時に決まった性別・特性を持つPokemonの原本を持つ
# 対戦のたびにbuild()で原本を複製して使うので、対戦が終わればHP・PP・状態は元に戻る（3節の「勝ち→全回復」）
@dataclass
class FactoryMon:
    set_ref: SetRef
    level: int
    iv: int
    template: Pokemon = field(repr=False)

    @property
    def name(self) -> str:
        return self.set_ref.name

    def build(self) -> Pokemon:
        return copy.deepcopy(self.template)


def make_mon(set_ref: SetRef, level: int, iv: int, rng: random.Random) -> FactoryMon:
    template = Pokemon(set_ref.pokemon_id, set_ref.indivisual_id, level=level, iv=iv, rng=rng)
    return FactoryMon(set_ref=set_ref, level=level, iv=iv, template=template)


# 候補sourcesから、種族も持ち物も互いに重ならないようにcount体を選ぶ（種族クローズ・アイテムクローズ）
# excluded_species/excluded_itemsに含まれる種族（図鑑番号）・持ち物は選ばない。
# sourcesは(セットの候補リスト, 個体値)の並びで、i体目はsources[i]から選ぶ（強いポケモン・前の周のポケモンを混ぜるため）
def pick_with_clauses(rng: random.Random, sources: List[tuple], level: int,
                      excluded_species: Iterable[int] = (), excluded_items: Iterable[Optional[int]] = ()) -> List[FactoryMon]:
    used_species: Set[int] = set(excluded_species)
    used_items: Set[Optional[int]] = set(excluded_items)
    picked = []
    for candidates, iv in sources:
        allowed = [s for s in candidates if s.dex_no not in used_species and s.item not in used_items]
        if not allowed:
            raise ValueError("種族・持ち物が重ならないセットを選べませんでした（プールが小さすぎます）")
        chosen = rng.choice(allowed)
        used_species.add(chosen.dex_no)
        used_items.add(chosen.item)
        picked.append(make_mon(chosen, level, iv, rng))
    return picked


class FactoryGenerator:
    def __init__(self, level: str, pool: Optional[SetPool] = None):
        self.level = level
        self.battle_level = rules.BATTLE_LEVELS[level]
        self.pool = pool if pool is not None else SetPool()

    # round_number周目のセット候補と個体値
    def round_source(self, round_number: int) -> tuple:
        spec = rules.pool_spec(self.level, round_number)
        return self.pool.select(spec, round_number), rules.iv_for_round(round_number)

    # 4節・6.3節: 周の開始時のレンタル候補6体。うちstrong_rental_count体は次の周の技構成・個体値で生成する
    def generate_rentals(self, rng: random.Random, round_number: int, rent_trade_count: int) -> List[FactoryMon]:
        strong = rules.strong_rental_count(rent_trade_count)
        sources = ([self.round_source(round_number + 1)] * strong
                   + [self.round_source(round_number)] * (rules.RENTAL_CANDIDATES - strong))
        rentals = pick_with_clauses(rng, sources, self.battle_level)
        # 強いポケモンが先頭に固まらないように並びを混ぜる
        rng.shuffle(rentals)
        return rentals

    # 6.4節・8節: battle_number戦目（連勝の通算。1始まり）の相手チーム3体。並び順の先頭が先発
    # 第1〜6戦は現在の周か1つ前の周のデータ、第7戦は次の周のデータで生成する。ネジキ戦は8節の表に従う
    # 相手チームはプレイヤーのチームと同じ種族・同じ持ち物を含まない（5節）
    def generate_opponents(self, rng: random.Random, battle_number: int, player_team: List[FactoryMon]) -> List[FactoryMon]:
        win_streak = battle_number - 1
        round_number = rules.round_of(win_streak)
        battle_in_round = rules.battle_in_round_of(win_streak)

        brain = rules.brain_battle(battle_number)
        if brain is not None:
            sources = [(self.pool.select(brain.pool, round_number), brain.iv)] * rules.TEAM_SIZE
        elif battle_in_round == rules.BATTLES_PER_ROUND:
            sources = [self.round_source(round_number + 1)] * rules.TEAM_SIZE
        else:
            # 「現在の周か1つ前の周」をどう混ぜるかは仕様が無いので、1体ごとに1/2で選ぶ（推測。READMEに記載）
            sources = []
            for _ in range(rules.TEAM_SIZE):
                source_round = round_number - 1 if round_number > 1 and rng.random() < 0.5 else round_number
                sources.append(self.round_source(source_round))

        return pick_with_clauses(
            rng, sources, self.battle_level,
            excluded_species=[mon.set_ref.dex_no for mon in player_team],
            excluded_items=[mon.set_ref.item for mon in player_team],
        )

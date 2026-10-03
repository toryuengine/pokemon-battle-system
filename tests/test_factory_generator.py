import random

import pytest

from factory import rules
from factory.generator import FactoryGenerator
from factory.hints import make_hint, most_common_type
from factory.pool import SetPool


def assert_clauses(team):
    assert len({mon.set_ref.dex_no for mon in team}) == len(team)
    assert len({mon.set_ref.item for mon in team}) == len(team)


def test_pool_select_variation():
    pool = SetPool()
    selected = pool.select(rules.PoolSpec(group=2, variations=(3,), legendary=False))
    assert len(selected) == 136
    assert all(s.variation == 3 for s in selected)


# グループ1のデータが無い間は、グループ2のバリエーションで代用する
def test_pool_group1_fallback():
    pool = SetPool()
    for round_number, variation in rules.GROUP1_FALLBACK_VARIATIONS.items():
        selected = pool.select(rules.pool_spec(rules.LEVEL_50, round_number), round_number)
        assert selected and all(s.group == 2 and s.variation == variation[0] for s in selected)


@pytest.mark.parametrize("level", [rules.LEVEL_50, rules.LEVEL_OPEN])
def test_rentals_follow_clauses_and_level(level):
    generator = FactoryGenerator(level)
    for seed in range(30):
        rentals = generator.generate_rentals(random.Random(seed), round_number=2, rent_trade_count=1)
        assert len(rentals) == 6
        assert_clauses(rentals)
        assert all(mon.level == rules.BATTLE_LEVELS[level] for mon in rentals)
        assert all(mon.iv == rules.iv_for_round(2) for mon in rentals)


# 累計14回なら、6体のうち2体が次の周の個体値・バリエーションになる
def test_strong_rentals_use_next_round():
    generator = FactoryGenerator(rules.LEVEL_OPEN)
    rentals = generator.generate_rentals(random.Random(0), round_number=2, rent_trade_count=14)
    assert sorted(mon.iv for mon in rentals) == [4, 4, 4, 4, 8, 8]
    for mon in rentals:
        assert mon.set_ref.variation == (3 if mon.iv == 8 else 2)


def test_opponents_exclude_player_species_and_items():
    generator = FactoryGenerator(rules.LEVEL_50)
    for seed in range(30):
        rng = random.Random(seed)
        player = generator.generate_rentals(rng, 1, 1)[:3]
        opponents = generator.generate_opponents(rng, battle_number=3, player_team=player)
        assert_clauses(player + opponents)


def test_opponents_round_sources():
    generator = FactoryGenerator(rules.LEVEL_OPEN)
    rng = random.Random(0)
    player = generator.generate_rentals(rng, 3, 1)[:3]
    ivs = set()
    for _ in range(30):
        # 3周目の第1〜6戦は、3周目か2周目のデータ
        ivs |= {mon.iv for mon in generator.generate_opponents(rng, battle_number=16, player_team=player)}
        # 4周目の第7戦（28戦目）は次の周（5周目）のデータ
        assert {mon.iv for mon in generator.generate_opponents(rng, battle_number=28, player_team=player)} == {16}
    assert ivs == {4, 8}


def test_brain_teams():
    generator = FactoryGenerator(rules.LEVEL_50)
    rng = random.Random(0)
    player = generator.generate_rentals(rng, 3, 1)[:3]
    silver = generator.generate_opponents(rng, battle_number=21, player_team=player)
    assert all(mon.iv == 12 and mon.set_ref.variation == 1 for mon in silver)
    gold = generator.generate_opponents(rng, battle_number=49, player_team=player)
    assert all(mon.iv == 31 and mon.set_ref.variation == 4 for mon in gold)


def test_hints_by_round():
    generator = FactoryGenerator(rules.LEVEL_50)
    team = generator.generate_rentals(random.Random(1), 1, 1)[:3]
    names = tuple(mon.name for mon in team)
    assert make_hint(1, team).names == names
    assert make_hint(2, team).names == names[:2]
    first_move = team[0].template.moves[0].name
    assert make_hint(3, team).names == names[:1] and make_hint(3, team).lead_move == first_move
    hint4 = make_hint(4, team)
    assert hint4.names == () and hint4.lead_move == first_move
    hint5 = make_hint(5, team)
    assert hint5.names == () and hint5.most_common_type == most_common_type(team)
    for round_number in range(1, 6):
        assert make_hint(round_number, team).describe()


def test_most_common_type_tiebreak():
    generator = FactoryGenerator(rules.LEVEL_50)
    pool = generator.pool.sets

    def mon_named(name):
        set_ref = next(s for s in pool if s.name == name)
        from factory.generator import make_mon
        return make_mon(set_ref, 50, 0, random.Random(0))

    # リザードン(ほのお/ひこう)・ギャラドス(みず/ひこう)・カメックス(みず): みず2・ひこう2 → ひこうが内部番号で先
    assert most_common_type([mon_named("リザードン"), mon_named("ギャラドス"), mon_named("カメックス")]) == "ひこう"
    # 全部1つずつなら、ノーマルが最優先
    assert most_common_type([mon_named("ケッキング"), mon_named("ゲンガー"), mon_named("バンギラス")]) == "ノーマル"

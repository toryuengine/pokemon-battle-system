import random

import pytest

from nature import NATURE_NAMES, NATURES, STAT_KEYS, calc_stat, calc_stats
from pokemon import Pokemon
from readpokemondata import load_pokemon_data


def all_sets():
    for pokemon_id, entry in enumerate(load_pokemon_data()):
        for indivisual_id, set_data in enumerate(entry["indivisual"]):
            yield pokemon_id, indivisual_id, entry, set_data


# 以前のデータ（実数値をLv.100・個体値0で持っていた）の値と、種族値・努力値・性格から計算した値が一致すること
@pytest.mark.parametrize("name, indivisual_id, expected", [
    ("フシギバナ", 0, {"hp": 270, "atk": 152, "def": 171, "spatk": 294, "spdef": 268, "spd": 165}),
    ("フシギバナ", 1, {"hp": 312, "atk": 152, "def": 234, "spatk": 205, "spdef": 247, "spd": 165}),
    ("フシギバナ", 2, {"hp": 270, "atk": 255, "def": 171, "spatk": 184, "spdef": 268, "spd": 165}),
    ("フシギバナ", 3, {"hp": 333, "atk": 152, "def": 171, "spatk": 294, "spdef": 205, "spd": 165}),
])
def test_calculated_stats_match_previous_data(name, indivisual_id, expected):
    pokemon_id = next(i for i, entry in enumerate(load_pokemon_data()) if entry["name"] == name)
    status = Pokemon(pokemon_id, indivisual_id, level=100, iv=0, rng=random.Random(0)).status
    assert (status.hp, status.atk, status.defense, status.spatk, status.spdef, status.spd) == tuple(expected[key] for key in STAT_KEYS)


# フロンティアの努力値は選んだ能力に510を均等に振る形（合計510以下・1能力255以下）
def test_ev_follows_frontier_pattern():
    for _, _, entry, set_data in all_sets():
        values = [value for value in set_data["ev"].values() if value > 0]
        assert len(set(values)) == 1, entry["name"]
        assert values[0] == min(255, 510 // len(values))
        assert set(set_data["ev"]) == set(STAT_KEYS)


# データの性格は性格ID（がんばりや=0〜きまぐれ=24）で持っている
def test_nature_ids():
    assert len(NATURE_NAMES) == 25
    assert NATURE_NAMES[0] == "がんばりや" and NATURE_NAMES[3] == "いじっぱり" and NATURE_NAMES[15] == "ひかえめ"
    assert NATURE_NAMES[24] == "きまぐれ"
    for _, _, entry, set_data in all_sets():
        assert 0 <= set_data["nature"] < len(NATURES), entry["name"]


# 実数値の計算式の検算（ガブリアス: 種族値108/130/95/80/85/102、ようき・攻撃と素早さに255）
@pytest.mark.parametrize("level, iv, expected", [
    (50, 31, {"hp": 183, "atk": 182, "def": 115, "spatk": 90, "spdef": 105, "spd": 169}),
    (100, 31, {"hp": 357, "atk": 359, "def": 226, "spatk": 176, "spdef": 206, "spd": 333}),
])
def test_calc_stats_garchomp(level, iv, expected):
    base = {"hp": 108, "atk": 130, "def": 95, "spatk": 80, "spdef": 85, "spd": 102}
    ev = {"hp": 0, "atk": 255, "def": 0, "spatk": 0, "spdef": 0, "spd": 255}
    assert calc_stats(base, ev, iv=iv, level=level, nature="ようき") == expected


def test_neutral_nature_has_no_modifier():
    assert calc_stat("atk", 100, 0, 0, 100, "まじめ") == 205


def test_pokemon_uses_level_and_iv():
    default = Pokemon(0, 0, rng=random.Random(0))
    assert default.level == 100
    assert default.status.hp == 270

    lv50 = Pokemon(0, 0, level=50, iv=31, rng=random.Random(0))
    assert lv50.level == 50
    assert lv50.status.hp < default.status.hp
    assert lv50.current_status.current_hp == lv50.status.hp


def test_pokemon_rng_makes_gender_and_ability_reproducible():
    first = [(p.gender, p.ability.id) for p in (Pokemon(i, 0, rng=random.Random(42)) for i in range(20))]
    second = [(p.gender, p.ability.id) for p in (Pokemon(i, 0, rng=random.Random(42)) for i in range(20))]
    assert first == second

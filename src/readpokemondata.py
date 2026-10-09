
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

_pokemon_data = None
_round_pools = None
_nejiki_pools = None
_move_data = None
_type_data = None
_type_chart_data = None
_ability_data = None
_item_data = None
_base_stats_data = None


def _load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# オープンレベルの周ごとのプールの定義（仕様書6.1・8節）
# "rounds"：周の番号（0=1周目）→ 周の名前と、その周で使うセットのグループ（data/pokemon.jsonの"group"）。
#   グループ4〜7はグループ2のバリエーション1〜4、グループ8は伝説（全バリエーション）。最後の項目は「5周目以降」
# "nejiki"：ネジキ戦（"silver"=21戦目、"gold"=49戦目）で使うグループ。ネジキ戦は周の第7戦を置き換える
def load_round_data(path=DATA_DIR / "round.json"):
    return _load_json(path)


# 全種族・全セットのデータ（Pokemon(pokemon_id, indivisual_id)はこのリストの位置で指定する）
# data/pokemon.jsonはセットしか持たないので、種族名(pokemon_name.json)と種族ごとの情報(species.json:
# 図鑑番号・メスになる確率・伝説か)、種族値・体重(base_stats.json。図鑑番号で引く)を合わせる。
# セットの並びはバリエーション番号の順（バリエーション1が0番目…）
def load_pokemon_data():
    global _pokemon_data
    if _pokemon_data is None:
        _pokemon_data = _build_pokemon_data()
    return _pokemon_data


# 周ごとに出てくるセットの一覧。(pokemon_id, indivisual_id)のリストで返す
# その周のグループ（round.jsonの"groups"）に入っているセットを集める。
# round.jsonに無い先の周（6周目以降）は、最後の項目（5周目以降）のプールになる
def load_round_pool(round_index: int):
    global _round_pools
    if _round_pools is None:
        _round_pools = _build_round_pools()
    return _round_pools[min(round_index, len(_round_pools) - 1)]


# ネジキ戦（"silver"=21戦目・"gold"=49戦目）で出てくるセットの一覧
def load_nejiki_pool(kind: str):
    global _nejiki_pools
    if _nejiki_pools is None:
        nejiki = load_round_data()["nejiki"]
        _nejiki_pools = {key: _sets_in_groups(nejiki[key]["groups"]) for key in nejiki}
    return _nejiki_pools[kind]


def _build_pokemon_data():
    names = _load_json(DATA_DIR / "pokemon_name.json")
    species = _load_json(DATA_DIR / "species.json")
    base_stats = load_base_stats_data()

    raw_entries = _load_json(DATA_DIR / "pokemon.json")
    # pokemon.jsonの"name"は種族ID。並びが種族IDの順になっていることを前提にリストの位置で引く
    assert [raw["name"] for raw in raw_entries] == list(range(len(names)))
    entries = []
    for raw in raw_entries:
        pokemon_id = raw["name"]
        entry = {
            "name": names[str(pokemon_id)],
            "type1": raw["type1"],
            "type2": raw["type2"],
            "ability": raw["ability"],
            **species[str(pokemon_id)],
            "indivisual": sorted(raw["indivisual"], key=lambda set_data: set_data["variation"]),
        }
        dex_entry = base_stats[str(entry["dex_no"])]
        # 種族値表(CSV由来)とpokemon.jsonで、種族名・タイプが食い違っていないか
        assert (dex_entry["name"], dex_entry["type1"], dex_entry["type2"]) == \
            (entry["name"], entry["type1"], entry["type2"]), entry["name"]
        entry["base_stats"] = dex_entry["base_stats"]
        entry["weight"] = dex_entry["weight"]
        entries.append(entry)
    return entries


# 指定したグループ（data/pokemon.jsonの"group"）に入っているセットを集める
def _sets_in_groups(groups):
    groups = set(groups)
    return [(pokemon_id, indivisual_id)
            for pokemon_id, entry in enumerate(load_pokemon_data())
            for indivisual_id, set_data in enumerate(entry["indivisual"])
            if set_data["group"] in groups]


def _build_round_pools():
    entries = load_pokemon_data()
    rounds = load_round_data()["rounds"]
    pools = [_sets_in_groups(rounds[str(round_index)]["groups"]) for round_index in range(len(rounds))]
    used = {pokemon_id for pool in pools for pokemon_id, _ in pool}
    missing = [entry["name"] for pokemon_id, entry in enumerate(entries) if pokemon_id not in used]
    assert not missing, f"どの周にも出てこない種族があります: {missing}"
    return pools


# 図鑑番号（文字列）→ 種族名・タイプ・種族値・体重（第4世代の全493種。data/base_stats.csv・weight.csvから tools/build_base_stats.py で作る）
# ファクトリーに出てこない種族も入っている（グループ1のデータを足すときなどに使う）
def load_base_stats_data(path=DATA_DIR / "base_stats.json"):
    global _base_stats_data
    if _base_stats_data is None:
        _base_stats_data = _load_json(path)
    return _base_stats_data


def load_move_data(path=DATA_DIR / "move.json"):
    global _move_data
    if _move_data is None:
        _move_data = _load_json(path)
    return _move_data


def load_type_data(path=DATA_DIR / "type.json"):
    global _type_data
    if _type_data is None:
        _type_data = _load_json(path)
    return _type_data


def load_type_chart_data(path=DATA_DIR / "type_chart.json"):
    global _type_chart_data
    if _type_chart_data is None:
        _type_chart_data = _load_json(path)
    return _type_chart_data


def load_ability_data(path=DATA_DIR / "ability.json"):
    global _ability_data
    if _ability_data is None:
        _ability_data = _load_json(path)
    return _ability_data


def load_item_data(path=DATA_DIR / "item.json"):
    global _item_data
    if _item_data is None:
        _item_data = _load_json(path)
    return _item_data

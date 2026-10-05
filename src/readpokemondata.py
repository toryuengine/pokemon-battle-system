
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

_pokemon_data = None
_round_pools = None
_move_data = None
_type_data = None
_type_chart_data = None
_ability_data = None
_item_data = None


def _load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# 周の番号（data/pokemon_<番号>.jsonの番号）→ 周の名前（"1周目"・"銀ネジキ"等）
def load_round_data(path=DATA_DIR / "round.json"):
    return _load_json(path)


# 周ごとに出てくるポケモンの元データ（data/pokemon_<番号>.json）。種族ごとに、その周で使われるセットだけが入っている
def load_round_pokemon_data(round_index: int):
    return _load_json(DATA_DIR / f"pokemon_{round_index}.json")


# 全種族・全セットをまとめたデータ（Pokemon(pokemon_id, indivisual_id)はこのリストの位置で指定する）
# 周ごとのファイルにはセットしか入っていないので、種族名(pokemon_name.json)と種族ごとの情報(species.json:
# 種族値・図鑑番号・メスになる確率・伝説か)を合わせ、全周のセットを重複なく並べ直す。
# セットの並びは「初めて出てくる周の順」（1周目のセットが0番目、2周目で増えたセットが1番目…）
def load_pokemon_data():
    global _pokemon_data
    if _pokemon_data is None:
        _pokemon_data = _build_pokemon_data()
    return _pokemon_data


# 周ごとに出てくるセットの一覧。(pokemon_id, indivisual_id)のリストで返す
def load_round_pool(round_index: int):
    global _round_pools
    if _round_pools is None:
        load_pokemon_data()
    return _round_pools[round_index]


# セットを見分けるためのキー（同じ種族で、技・持ち物・性格・努力値が全て同じなら同じセット）
def _set_key(set_data):
    return (tuple(set_data["move"]), set_data["item"], set_data["nature"], tuple(sorted(set_data["ev"].items())))


def _build_pokemon_data():
    global _round_pools
    names = _load_json(DATA_DIR / "pokemon_name.json")
    species = _load_json(DATA_DIR / "species.json")

    entries = [None] * len(names)
    set_index = [dict() for _ in names]
    rounds = []
    for round_index in range(len(load_round_data())):
        pool = []
        for raw in load_round_pokemon_data(round_index):
            pokemon_id = raw["name"]
            entry = entries[pokemon_id]
            if entry is None:
                entry = {
                    "name": names[str(pokemon_id)],
                    "type1": raw["type1"],
                    "type2": raw["type2"],
                    "ability": raw["ability"],
                    **species[str(pokemon_id)],
                    "indivisual": [],
                }
                entries[pokemon_id] = entry
            # 種族の情報はどの周のファイルでも同じはず
            assert (raw["type1"], raw["type2"], raw["ability"]) == (entry["type1"], entry["type2"], entry["ability"]), entry["name"]
            for set_data in raw["indivisual"]:
                key = _set_key(set_data)
                if key not in set_index[pokemon_id]:
                    set_index[pokemon_id][key] = len(entry["indivisual"])
                    entry["indivisual"].append(set_data)
                pool.append((pokemon_id, set_index[pokemon_id][key]))
        rounds.append(pool)

    missing = [names[str(i)] for i, entry in enumerate(entries) if entry is None]
    assert not missing, f"どの周にも出てこない種族があります: {missing}"
    _round_pools = rounds
    return entries


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

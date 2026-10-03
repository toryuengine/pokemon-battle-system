"""data/pokemon.json に、種族値・努力値・性格・グループ・バリエーション番号を書き足すスクリプト。

一度実行した結果を data/pokemon.json としてコミットしているので、普段は実行する必要はない。
データの出どころを追えるように残している。

入力（あらかじめダウンロードしておく）:
  --showdown-dir : Pokémon Showdown の data/pokedex.ts と data/mods/gen5〜7/pokedex.ts を置いたディレクトリ
                   （pokedex.ts, gen5dex.ts, gen6dex.ts, gen7dex.ts という名前で置く）
  --species-names: PokeAPI の data/v2/csv/pokemon_species_names.csv（日本語名→図鑑番号の対応に使う）

やっていること:
  1. 種族値は Showdown の現行値に、第7→第6→第5世代の差分(mods)を順に重ねて第4世代当時の値にする
     （第6世代以降に種族値が上がったポケモン（ライチュウ・フーディン等）を第4世代の値に戻すため）
  2. 既存の実数値（Lv.100・個体値0）から、努力値と性格を逆算する。
     バトルフロンティアのポケモンは努力値を選んだ能力に均等に振る（2能力なら255ずつ、3能力なら170ずつ…）ので、
     その形の努力値と25通りの性格を総当たりし、実数値がすべて一致する組がちょうど1つになることを確認する
  3. 既存の136種・各4セットはBulbapediaのグループ2の並び順と仮定し、group=2・variation=1〜4を付ける
"""
import argparse
import itertools
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from nature import NATURES, STAT_KEYS, calc_stats  # noqa: E402

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "pokemon.json"
SHOWDOWN_STAT_KEYS = ("hp", "atk", "def", "spa", "spd", "spe")
# 無補正の性格は実数値から区別できないので、便宜上この性格にする
NEUTRAL_NATURE = "まじめ"

BASE_STATS_PATTERN = re.compile(
    r"baseStats: \{ ?hp: (\d+), atk: (\d+), def: (\d+), spa: (\d+), spd: (\d+), spe: (\d+) ?\}")


def parse_showdown_pokedex(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    entries = {}
    for match in re.finditer(r"\n\t(\w+): \{(.*?)\n\t\}", text, re.S):
        key, body = match.group(1), match.group(2)
        num = re.search(r"\bnum: (-?\d+)", body)
        base_stats = BASE_STATS_PATTERN.search(body)
        entries[key] = {
            "num": int(num.group(1)) if num else None,
            "base_stats": tuple(map(int, base_stats.groups())) if base_stats else None,
        }
    return entries


def load_gen4_base_stats(showdown_dir: Path) -> dict:
    current = parse_showdown_pokedex(showdown_dir / "pokedex.ts")
    # 古い世代ほど先に見る（gen5のmodsが第5世代＝第4世代と同じ値を持つ）
    mods = [parse_showdown_pokedex(showdown_dir / f"gen{gen}dex.ts") for gen in (5, 6, 7)]

    key_by_num = {}
    for key, entry in current.items():
        if entry["num"] and entry["num"] > 0 and entry["num"] not in key_by_num:
            key_by_num[entry["num"]] = key

    result = {}
    for num, key in key_by_num.items():
        base_stats = next((mod[key]["base_stats"] for mod in mods
                           if key in mod and mod[key]["base_stats"]), current[key]["base_stats"])
        result[num] = dict(zip(STAT_KEYS, base_stats))
    return result


def load_dex_numbers(species_names_csv: Path) -> dict:
    import csv
    numbers = {}
    with open(species_names_csv, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            # 1: 日本語（カタカナ）、11: 日本語
            if row["local_language_id"] in ("1", "11"):
                numbers[unicodedata.normalize("NFKC", row["name"])] = int(row["pokemon_species_id"])
    return numbers


# フロンティアの努力値の振り方（選んだ能力に510を均等割り、1能力の上限255）の候補をすべて返す
def frontier_ev_patterns():
    for count in range(1, 7):
        value = min(255, 510 // count)
        for chosen in itertools.combinations(STAT_KEYS, count):
            yield {key: (value if key in chosen else 0) for key in STAT_KEYS}


def infer_ev_and_nature(base_stats: dict, actual: dict):
    solutions = []
    natures = [name for name, (up, _) in NATURES.items() if up is not None] + [NEUTRAL_NATURE]
    for ev in frontier_ev_patterns():
        for nature in natures:
            if calc_stats(base_stats, ev, iv=0, level=100, nature=nature) == actual:
                solutions.append((ev, nature))
    return solutions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--showdown-dir", type=Path, required=True)
    parser.add_argument("--species-names", type=Path, required=True)
    args = parser.parse_args()

    base_stats_by_num = load_gen4_base_stats(args.showdown_dir)
    dex_numbers = load_dex_numbers(args.species_names)
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    for entry in data:
        dex_no = dex_numbers[unicodedata.normalize("NFKC", entry["name"])]
        base_stats = base_stats_by_num[dex_no]
        new_entry = {
            "name": entry["name"],
            "dex_no": dex_no,
            "type1": entry["type1"],
            "type2": entry["type2"],
            "female_rate": entry["female_rate"],
            "ability": entry["ability"],
            "base_stats": base_stats,
            "legendary": entry.get("legendary", False),
        }
        for variation, set_data in enumerate(entry["indivisual"], start=1):
            actual = {key: set_data["status"][key] for key in STAT_KEYS}
            solutions = infer_ev_and_nature(base_stats, actual)
            if len(solutions) != 1:
                raise ValueError(f"{entry['name']}の{variation}番目のセットの努力値・性格が一意に決まりません: {solutions}")
            ev, nature = solutions[0]
            set_data["group"] = 2
            set_data["variation"] = variation
            set_data["nature"] = nature
            set_data["ev"] = ev
        new_entry["indivisual"] = entry["indivisual"]
        entry.clear()
        entry.update(new_entry)

    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

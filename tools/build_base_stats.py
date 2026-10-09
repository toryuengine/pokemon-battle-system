"""data/base_stats.csv（ユーザーが作った第4世代の全493種の種族値表）と data/weight.csv（体重）から
data/base_stats.json を作るスクリプト。

CSVを直したらこのスクリプトを実行し直す（src/ と同じ階層から `python tools/build_base_stats.py`）。
コードは data/base_stats.json だけを読むので、CSVはデータの元として残している。

出力の形（キーは図鑑番号。1〜493）:
  "3": {"name": "フシギバナ", "type1": 4, "type2": 7,
        "base_stats": {"hp": 80, "atk": 82, "def": 83, "spatk": 100, "spdef": 100, "spd": 80},
        "weight": 100.0}
- タイプは data/type.json のID（単タイプなら type2 は null。周ごとのポケモンデータと同じ持ち方）
- 合計値（total）は種族値から計算できるので持たない。代わりに、CSVの合計と一致するかを確かめる
- 体重はkg（くさむすびの威力に使う）。data/weight.csv は PokeAPI のデータ
  （https://github.com/PokeAPI/pokeapi の data/v2/csv/pokemon.csv。図鑑番号1〜493の通常の姿）から作った
"""
import csv
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
STAT_KEYS = ("hp", "atk", "def", "spatk", "spdef", "spd")


def main():
    type_ids = {name: int(type_id) for type_id, name in
                json.loads((DATA_DIR / "type.json").read_text(encoding="utf-8")).items()}

    weights = {}
    with open(DATA_DIR / "weight.csv", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            weights[int(row["dex_no"])] = (row["name"], float(row["weight"]))

    result = {}
    # Excel等で保存したCSVは先頭にBOMが付くので utf-8-sig で読む
    with open(DATA_DIR / "base_stats.csv", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            dex_no = int(row["dex_no"])
            base_stats = {key: int(row[key]) for key in STAT_KEYS}
            if sum(base_stats.values()) != int(row["total"]):
                raise ValueError(f"{row['name']}の種族値の合計がCSVのtotalと一致しません")
            if str(dex_no) in result:
                raise ValueError(f"図鑑番号{dex_no}が重複しています")
            result[str(dex_no)] = {
                "name": row["name"],
                "type1": type_ids[row["type1"]],
                "type2": type_ids[row["type2"]] if row["type2"] else None,
                "base_stats": base_stats,
            }
            weight_name, weight = weights[dex_no]
            if weight_name != row["name"]:
                raise ValueError(f"図鑑番号{dex_no}の種族名が体重のCSVと一致しません")
            result[str(dex_no)]["weight"] = weight

    if sorted(map(int, result)) != list(range(1, 494)):
        raise ValueError("図鑑番号1〜493がそろっていません")
    (DATA_DIR / "base_stats.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

# 性格と、能力の実数値の計算（第3世代以降共通の計算式）

STAT_KEYS = ("hp", "atk", "def", "spatk", "spdef", "spd")

# 性格名 → (1.1倍になる能力, 0.9倍になる能力)。無補正の性格は(None, None)
# HPは性格の影響を受けない
NATURES = {
    "がんばりや": (None, None),
    "さみしがり": ("atk", "def"),
    "ゆうかん": ("atk", "spd"),
    "いじっぱり": ("atk", "spatk"),
    "やんちゃ": ("atk", "spdef"),
    "ずぶとい": ("def", "atk"),
    "すなお": (None, None),
    "のんき": ("def", "spd"),
    "わんぱく": ("def", "spatk"),
    "のうてんき": ("def", "spdef"),
    "おくびょう": ("spd", "atk"),
    "せっかち": ("spd", "def"),
    "まじめ": (None, None),
    "ようき": ("spd", "spatk"),
    "むじゃき": ("spd", "spdef"),
    "ひかえめ": ("spatk", "atk"),
    "おっとり": ("spatk", "def"),
    "れいせい": ("spatk", "spd"),
    "てれや": (None, None),
    "うっかりや": ("spatk", "spdef"),
    "おだやか": ("spdef", "atk"),
    "おとなしい": ("spdef", "def"),
    "なまいき": ("spdef", "spd"),
    "しんちょう": ("spdef", "spatk"),
    "きまぐれ": (None, None),
}

# 性格ID → 性格名。データ（pokemon_<周>.jsonの"nature"）は性格を本編の性格ID（がんばりや=0〜きまぐれ=24）で持っていて、
# NATURESはその順に並べてある
NATURE_NAMES = list(NATURES)


# 上昇・下降する能力の組から性格名を引く（無補正ならNoneを返す。無補正の5種は実数値から区別できないため）
def find_nature(up, down):
    if up is None:
        return None
    for name, (nature_up, nature_down) in NATURES.items():
        if nature_up == up and nature_down == down:
            return name
    raise ValueError(f"該当する性格がありません: up={up}, down={down}")


# 1つの能力の実数値を計算する（第3世代以降の計算式。端数は各段階で切り捨て）
#   HP     = (種族値×2 + 個体値 + 努力値/4) × レベル/100 + レベル + 10
#   HP以外 = ((種族値×2 + 個体値 + 努力値/4) × レベル/100 + 5) × 性格補正
def calc_stat(key: str, base: int, iv: int, ev: int, level: int, nature: str) -> int:
    value = (2 * base + iv + ev // 4) * level // 100
    if key == "hp":
        return value + level + 10
    up, down = NATURES[nature]
    # 性格補正は×1.1/×0.9を整数で計算する（本編同様、小数を使わず110/100・90/100で切り捨て）
    if key == up:
        return (value + 5) * 110 // 100
    if key == down:
        return (value + 5) * 90 // 100
    return value + 5


# 6能力すべての実数値を計算し、{"hp": ..., "atk": ..., ...}の形で返す
def calc_stats(base_stats: dict, ev: dict, iv: int, level: int, nature: str) -> dict:
    return {key: calc_stat(key, base_stats[key], iv, ev[key], level, nature) for key in STAT_KEYS}

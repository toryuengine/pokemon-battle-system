from move.base_move import CATEGORY_PHYSICAL, CATEGORY_SPECIAL

# 持ち物のID（data/item.jsonのキー）。効果は第4世代仕様に合わせている
WHITE_HERB = 0  # しろいハーブ: 能力ランクが下がると、下がったランクを元に戻す（1回で消費）
BIG_ROOT = 1  # おおきなねっこ: 吸収技の回復量が1.3倍
BLACK_SLUDGE = 2  # くろいヘドロ: どくタイプなら毎ターン1/16回復、それ以外は1/8ダメージ
WISE_GLASSES = 3  # ものしりメガネ: 特殊技の威力1.1倍
PETAYA_BERRY = 4  # ヤタピのみ: HP1/4以下で特攻+1
SCOPE_LENS = 5  # ピントレンズ: 急所ランク+1
BRIGHT_POWDER = 6  # ひかりのこな: 相手の技の命中率0.9倍
MYSTIC_WATER = 7  # しんぴのしずく: みず技の威力1.2倍
SHELL_BELL = 8  # かいがらのすず: 与えたダメージの1/8回復
LIFE_ORB = 9  # いのちのたま: ダメージ1.3倍、攻撃するたびに最大HPの1/10を失う
HEAT_ROCK = 10  # あついいわ: にほんばれが8ターン続く
LIGHT_CLAY = 11  # ひかりのねんど: リフレクター・ひかりのかべが8ターン続く
LAX_INCENSE = 12  # のんきのおこう: 相手の技の命中率0.9倍
SALAC_BERRY = 13  # カムラのみ: HP1/4以下で素早さ+1
SHUCA_BERRY = 14  # シュカのみ: 効果抜群のじめん技のダメージ半減
KINGS_ROCK = 15  # おうじゃのしるし: ダメージ技に10%のひるみ効果
LUM_BERRY = 16  # ラムのみ: 状態異常・こんらんを回復
LIECHI_BERRY = 17  # チイラのみ: HP1/4以下で攻撃+1
LEFTOVERS = 18  # たべのこし: 毎ターン1/16回復
OCCA_BERRY = 19  # オッカのみ: 効果抜群のほのお技のダメージ半減
PASSHO_BERRY = 20  # イトケのみ: 効果抜群のみず技のダメージ半減
EXPERT_BELT = 21  # たつじんのおび: 効果抜群の技のダメージ1.2倍
RINDO_BERRY = 22  # リンドのみ: 効果抜群のくさ技のダメージ半減
YACHE_BERRY = 23  # ヤチェのみ: 効果抜群のこおり技のダメージ半減
QUICK_CLAW = 24  # せんせいのツメ: 20%の確率で同じ優先度の中で先に行動する
COBA_BERRY = 25  # バコウのみ: 効果抜群のひこう技のダメージ半減
MUSCLE_BAND = 26  # ちからのハチマキ: 物理技の威力1.1倍
RAZOR_CLAW = 27  # するどいツメ: 急所ランク+1
GRIP_CLAW = 28  # ねばりのかぎづめ: しめつけ系の技が5ターン続く（しめつけ系の技が未実装のため効果なし）
THICK_CLUB = 29  # ふといホネ: カラカラ・ガラガラの攻撃2倍
CHERI_BERRY = 30  # クラボのみ: まひを回復
CHESTO_BERRY = 31  # カゴのみ: ねむりを回復
CHOICE_SPECS = 32  # こだわりメガネ: 特攻1.5倍、最初に出した技しか出せなくなる
KASIB_BERRY = 33  # カシブのみ: 効果抜群のゴースト技のダメージ半減
SITRUS_BERRY = 34  # オボンのみ: HP1/2以下で最大HPの1/4回復
FOCUS_SASH = 35  # きあいのタスキ: HP満タンから一撃で倒される攻撃をHP1で耐える（1回で消費）
TOXIC_ORB = 36  # どくどくだま: ターン終了時にどく状態になる
CHOPLE_BERRY = 37  # ヨプのみ: 効果抜群のかくとう技のダメージ半減
CHOICE_BAND = 38  # こだわりハチマキ: 攻撃1.5倍、最初に出した技しか出せなくなる
PERSIM_BERRY = 39  # キーのみ: こんらんを回復
ZOOM_LENS = 40  # フォーカスレンズ: 相手より後に行動すると命中率1.2倍
IRON_BALL = 41  # くろいてっきゅう: 素早さ半減、ひこうタイプでもじめん技・まきびし等を受ける
WIDE_LENS = 42  # こうかくレンズ: 命中率1.1倍
FOCUS_BAND = 43  # きあいのハチマキ: 10%の確率で瀕死になる攻撃をHP1で耐える（消費しない）
RAZOR_FANG = 44  # するどいキバ: ダメージ技に10%のひるみ効果
WACAN_BERRY = 45  # ソクノのみ: 効果抜群のでんき技のダメージ半減
DAMP_ROCK = 46  # しめったいわ: あまごいが8ターン続く
PAYAPA_BERRY = 47  # ウタンのみ: 効果抜群のエスパー技のダメージ半減
POWER_HERB = 48  # パワフルハーブ: 溜め技の溜めターンを省略する（1回で消費）
METRONOME = 49  # メトロノーム: 同じ技を連続で使うたびに威力が1割ずつ上がる（最大2倍）
TANGA_BERRY = 50  # ナモのみ: 効果抜群のむし技のダメージ半減
SEA_INCENSE = 51  # さざなみのおこう: みず技の威力1.2倍
CHOICE_SCARF = 52  # こだわりスカーフ: 素早さ1.5倍、最初に出した技しか出せなくなる
ICY_ROCK = 53  # つめたいいわ: あられが8ターン続く

# 半減実の持ち物ID → 半減する技のタイプ
RESIST_BERRY_TYPES = {
    SHUCA_BERRY: "じめん",
    OCCA_BERRY: "ほのお",
    PASSHO_BERRY: "みず",
    RINDO_BERRY: "くさ",
    YACHE_BERRY: "こおり",
    COBA_BERRY: "ひこう",
    KASIB_BERRY: "ゴースト",
    CHOPLE_BERRY: "かくとう",
    WACAN_BERRY: "でんき",
    PAYAPA_BERRY: "エスパー",
    TANGA_BERRY: "むし",
}
RESIST_BERRY_MULTIPLIER = 0.5

# ピンチ実（HP1/4以下で能力ランク+1）の持ち物ID → 上がる能力
PINCH_BERRY_STATS = {
    LIECHI_BERRY: "atk",
    PETAYA_BERRY: "spatk",
    SALAC_BERRY: "spd",
}
PINCH_BERRY_HP_RATIO = 1 / 4
SITRUS_BERRY_HP_RATIO = 1 / 2
SITRUS_BERRY_HEAL_RATIO = 1 / 4

# 天候を伸ばす岩の持ち物ID → 伸びる天候
WEATHER_ROCKS = {
    HEAT_ROCK: "sun",
    DAMP_ROCK: "rain",
    ICY_ROCK: "hail",
}
EXTENDED_WEATHER_DURATION = 8
EXTENDED_SCREEN_DURATION = 8

CHOICE_ITEMS = {CHOICE_BAND, CHOICE_SPECS, CHOICE_SCARF}
CHOICE_STAT_MULTIPLIER = 1.5
CHOICE_SCARF_SPEED_MULTIPLIER = 1.5
IRON_BALL_SPEED_MULTIPLIER = 0.5

CRIT_BOOST_ITEMS = {SCOPE_LENS, RAZOR_CLAW}
FLINCH_ITEMS = {KINGS_ROCK, RAZOR_FANG}
FLINCH_ITEM_CHANCE = 0.1

# 相手の命中率を下げる持ち物
EVASION_ITEMS = {BRIGHT_POWDER, LAX_INCENSE}
EVASION_ITEM_MULTIPLIER = 0.9
WIDE_LENS_MULTIPLIER = 1.1
ZOOM_LENS_MULTIPLIER = 1.2

QUICK_CLAW_CHANCE = 0.2
FOCUS_BAND_CHANCE = 0.1

LEFTOVERS_HEAL_RATIO = 1 / 16
BLACK_SLUDGE_DAMAGE_RATIO = 1 / 8
BIG_ROOT_MULTIPLIER = 1.3
SHELL_BELL_RATIO = 1 / 8
LIFE_ORB_MULTIPLIER = 1.3
LIFE_ORB_RECOIL_RATIO = 1 / 10
EXPERT_BELT_MULTIPLIER = 1.2

METRONOME_BOOST_PER_USE = 0.1
METRONOME_MAX_MULTIPLIER = 2.0

# ふといホネの効果を受けられる種族
THICK_CLUB_POKEMON_NAMES = {"カラカラ", "ガラガラ"}
THICK_CLUB_MULTIPLIER = 2.0

TYPE_ID_FLYING = 9


# 物理・特殊技の威力を上げる持ち物の倍率（第4世代では技の威力に掛かる）
def get_item_power_multiplier(attacker, move) -> float:
    item = attacker.item
    if item == MUSCLE_BAND and move.category == CATEGORY_PHYSICAL:
        return 1.1
    if item == WISE_GLASSES and move.category == CATEGORY_SPECIAL:
        return 1.1
    if item in (MYSTIC_WATER, SEA_INCENSE) and move.type == "みず":
        return 1.2
    return 1.0


# 攻撃・特攻の実数値を上げる持ち物の倍率（こだわりハチマキ・こだわりメガネ・ふといホネ）
def get_item_attack_stat_multiplier(attacker, move) -> float:
    item = attacker.item
    if move.category == CATEGORY_PHYSICAL:
        if item == CHOICE_BAND:
            return CHOICE_STAT_MULTIPLIER
        if item == THICK_CLUB and attacker.name in THICK_CLUB_POKEMON_NAMES:
            return THICK_CLUB_MULTIPLIER
    elif move.category == CATEGORY_SPECIAL and item == CHOICE_SPECS:
        return CHOICE_STAT_MULTIPLIER
    return 1.0


# 最終ダメージに掛かる持ち物の倍率（いのちのたま・たつじんのおび）
def get_item_damage_multiplier(attacker, effectiveness: float) -> float:
    if attacker.item == LIFE_ORB:
        return LIFE_ORB_MULTIPLIER
    if attacker.item == EXPERT_BELT and effectiveness > 1:
        return EXPERT_BELT_MULTIPLIER
    return 1.0


# 持ち物による急所ランクの上昇量
def get_item_crit_stage_bonus(attacker) -> int:
    return 1 if attacker.item in CRIT_BOOST_ITEMS else 0


# くろいてっきゅうを持っていれば、ひこうタイプでも地面にいる扱いになる
def is_grounded(pokemon) -> bool:
    if pokemon.item == IRON_BALL:
        return True
    return TYPE_ID_FLYING not in (pokemon.type1, pokemon.type2)


# defenderの半減実が、この技で発動するかどうか（効果抜群の対応タイプの技で発動する）
def is_resist_berry_triggered(defender, move, effectiveness: float) -> bool:
    berry_type = RESIST_BERRY_TYPES.get(defender.item)
    if berry_type is None or move.is_typeless or effectiveness <= 1:
        return False
    return move.type == berry_type

from functools import partial

from item.accuracy import EvasionItem, WideLens, ZoomLens
from item.attack import CategoryBoostItem, CritBoostItem, ExpertBelt, FlinchItem, LifeOrb, Metronome, ThickClub, TypeBoostItem
from item.base_item import BaseItem
from item.berry import PinchBerry, ResistBerry, SitrusBerry, StatusCureBerry
from item.choice import ChoiceBand, ChoiceScarf, ChoiceSpecs
from item.duration import GripClaw, LightClay, WeatherRock
from item.herb import PowerHerb, WhiteHerb
from item.recovery import BigRoot, BlackSludge, Leftovers, ShellBell
from item.speed import IronBall, QuickClaw
from item.survival import FocusBand, FocusSash
from item.toxic_orb import ToxicOrb
from move.base_move import CATEGORY_PHYSICAL, CATEGORY_SPECIAL

# 持ち物ID（data/item.jsonのキー）→ 持ち物クラス。効果は第4世代仕様に合わせている
# 半減実のように効果が同じでパラメータだけ違う持ち物は、1つのクラスにpartialでパラメータを渡して使い回す
_ITEM_CLASSES = {
    0: WhiteHerb,  # しろいハーブ
    1: partial(PinchBerry, stat_name="spatk"),  # ヤタピのみ
    2: partial(TypeBoostItem, move_type="みず", multiplier=1.2),  # しんぴのしずく
    3: partial(WeatherRock, weather="sun"),  # あついいわ
    4: CritBoostItem,  # ピントレンズ
    5: FlinchItem,  # おうじゃのしるし
    6: partial(PinchBerry, stat_name="atk"),  # チイラのみ
    7: partial(PinchBerry, stat_name="spd"),  # カムラのみ
    8: ShellBell,  # かいがらのすず
    9: partial(ResistBerry, resist_type="こおり"),  # ヤチェのみ
    10: partial(ResistBerry, resist_type="ひこう"),  # バコウのみ
    11: CritBoostItem,  # するどいツメ
    12: GripClaw,  # ねばりのかぎづめ
    13: partial(ResistBerry, resist_type="くさ"),  # リンドのみ
    14: partial(StatusCureBerry, cures_conditions=("sleep",)),  # カゴのみ
    15: partial(StatusCureBerry, cures_conditions=("paralysis",)),  # クラボのみ
    16: FocusSash,  # きあいのタスキ
    17: partial(ResistBerry, resist_type="ほのお"),  # オッカのみ
    18: partial(ResistBerry, resist_type="かくとう"),  # ヨプのみ
    19: partial(StatusCureBerry, cures_confusion=True),  # キーのみ
    20: WideLens,  # こうかくレンズ
    21: FlinchItem,  # するどいキバ
    22: partial(ResistBerry, resist_type="じめん"),  # シュカのみ
    23: BigRoot,  # おおきなねっこ
    24: partial(ResistBerry, resist_type="エスパー"),  # ウタンのみ
    25: partial(CategoryBoostItem, category=CATEGORY_PHYSICAL, multiplier=1.1),  # ちからのハチマキ
    26: IronBall,  # くろいてっきゅう
    27: FocusBand,  # きあいのハチマキ
    28: partial(ResistBerry, resist_type="みず"),  # イトケのみ
    29: EvasionItem,  # ひかりのこな
    30: BlackSludge,  # くろいヘドロ
    31: partial(StatusCureBerry, cures_conditions=None, cures_confusion=True),  # ラムのみ
    32: SitrusBerry,  # オボンのみ
    33: partial(ResistBerry, resist_type="ゴースト"),  # カシブのみ
    34: EvasionItem,  # のんきのおこう
    35: ToxicOrb,  # どくどくだま
    36: partial(ResistBerry, resist_type="でんき"),  # ソクノのみ
    37: QuickClaw,  # せんせいのツメ
    38: Leftovers,  # たべのこし
    39: partial(WeatherRock, weather="hail"),  # つめたいいわ
    40: LightClay,  # ひかりのねんど
    41: PowerHerb,  # パワフルハーブ
    42: ThickClub,  # ふといホネ
    43: partial(WeatherRock, weather="rain"),  # しめったいわ
    44: ZoomLens,  # フォーカスレンズ
    45: LifeOrb,  # いのちのたま
    46: Metronome,  # メトロノーム
    47: ExpertBelt,  # たつじんのおび
    48: partial(ResistBerry, resist_type="むし"),  # ナモのみ
    49: partial(CategoryBoostItem, category=CATEGORY_SPECIAL, multiplier=1.1),  # ものしりメガネ
    50: ChoiceScarf,  # こだわりスカーフ
    51: ChoiceSpecs,  # こだわりメガネ
    52: ChoiceBand,  # こだわりハチマキ
    53: partial(TypeBoostItem, move_type="みず", multiplier=1.2),  # さざなみのおこう
    54: partial(ResistBerry, resist_type="いわ"),  # ヨロギのみ
}


# 持ち物IDから持ち物のインスタンスを作る。効果を持つクラスが登録されていなければ効果なしの持ち物として扱う
def create_item(item_id: int) -> BaseItem:
    item_class = _ITEM_CLASSES.get(item_id)
    if item_class is None:
        return BaseItem(item_id)
    return item_class(item_id)

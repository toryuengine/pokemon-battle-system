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
    1: BigRoot,  # おおきなねっこ
    2: BlackSludge,  # くろいヘドロ
    3: partial(CategoryBoostItem, category=CATEGORY_SPECIAL, multiplier=1.1),  # ものしりメガネ
    4: partial(PinchBerry, stat_name="spatk"),  # ヤタピのみ
    5: CritBoostItem,  # ピントレンズ
    6: EvasionItem,  # ひかりのこな
    7: partial(TypeBoostItem, move_type="みず", multiplier=1.2),  # しんぴのしずく
    8: ShellBell,  # かいがらのすず
    9: LifeOrb,  # いのちのたま
    10: partial(WeatherRock, weather="sun"),  # あついいわ
    11: LightClay,  # ひかりのねんど
    12: EvasionItem,  # のんきのおこう
    13: partial(PinchBerry, stat_name="spd"),  # カムラのみ
    14: partial(ResistBerry, resist_type="じめん"),  # シュカのみ
    15: FlinchItem,  # おうじゃのしるし
    16: partial(StatusCureBerry, cures_conditions=None, cures_confusion=True),  # ラムのみ
    17: partial(PinchBerry, stat_name="atk"),  # チイラのみ
    18: Leftovers,  # たべのこし
    19: partial(ResistBerry, resist_type="ほのお"),  # オッカのみ
    20: partial(ResistBerry, resist_type="みず"),  # イトケのみ
    21: ExpertBelt,  # たつじんのおび
    22: partial(ResistBerry, resist_type="くさ"),  # リンドのみ
    23: partial(ResistBerry, resist_type="こおり"),  # ヤチェのみ
    24: QuickClaw,  # せんせいのツメ
    25: partial(ResistBerry, resist_type="ひこう"),  # バコウのみ
    26: partial(CategoryBoostItem, category=CATEGORY_PHYSICAL, multiplier=1.1),  # ちからのハチマキ
    27: CritBoostItem,  # するどいツメ
    28: GripClaw,  # ねばりのかぎづめ
    29: ThickClub,  # ふといホネ
    30: partial(StatusCureBerry, cures_conditions=("paralysis",)),  # クラボのみ
    31: partial(StatusCureBerry, cures_conditions=("sleep",)),  # カゴのみ
    32: ChoiceSpecs,  # こだわりメガネ
    33: partial(ResistBerry, resist_type="ゴースト"),  # カシブのみ
    34: SitrusBerry,  # オボンのみ
    35: FocusSash,  # きあいのタスキ
    36: ToxicOrb,  # どくどくだま
    37: partial(ResistBerry, resist_type="かくとう"),  # ヨプのみ
    38: ChoiceBand,  # こだわりハチマキ
    39: partial(StatusCureBerry, cures_confusion=True),  # キーのみ
    40: ZoomLens,  # フォーカスレンズ
    41: IronBall,  # くろいてっきゅう
    42: WideLens,  # こうかくレンズ
    43: FocusBand,  # きあいのハチマキ
    44: FlinchItem,  # するどいキバ
    45: partial(ResistBerry, resist_type="でんき"),  # ソクノのみ
    46: partial(WeatherRock, weather="rain"),  # しめったいわ
    47: partial(ResistBerry, resist_type="エスパー"),  # ウタンのみ
    48: PowerHerb,  # パワフルハーブ
    49: Metronome,  # メトロノーム
    50: partial(ResistBerry, resist_type="むし"),  # ナモのみ
    51: partial(TypeBoostItem, move_type="みず", multiplier=1.2),  # さざなみのおこう
    52: ChoiceScarf,  # こだわりスカーフ
    53: partial(WeatherRock, weather="hail"),  # つめたいいわ
}


# 持ち物IDから持ち物のインスタンスを作る。効果を持つクラスが登録されていなければ効果なしの持ち物として扱う
def create_item(item_id: int) -> BaseItem:
    item_class = _ITEM_CLASSES.get(item_id)
    if item_class is None:
        return BaseItem(item_id)
    return item_class(item_id)

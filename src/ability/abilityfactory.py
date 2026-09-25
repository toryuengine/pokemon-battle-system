from ability.base_ability import BaseAbility
from ability.ability_000 import Overgrow
from ability.ability_001 import Blaze
from ability.ability_002 import Torrent
from ability.ability_003 import SandVeil
from ability.ability_004 import ArenaTrap
from ability.ability_005 import RockHead
from ability.ability_006 import LightningRod
from ability.ability_007 import PurePower
from ability.ability_008 import Damp
from ability.ability_009 import WaterAbsorb
from ability.ability_010 import Intimidate
from ability.ability_011 import QuickFeet
from ability.ability_012 import Oblivious
from ability.ability_013 import Forewarn
from ability.ability_014 import Soundproof
from ability.ability_015 import Filter
from ability.ability_016 import VoltAbsorb
from ability.ability_017 import Illuminate
from ability.ability_018 import EffectSpore
from ability.ability_019 import PoisonHeal
from ability.ability_020 import Sturdy
from ability.ability_021 import KeenEye
from ability.ability_022 import Pressure
from ability.ability_023 import SuperLuck
from ability.ability_024 import Anticipation
from ability.ability_025 import ThickFat
from ability.ability_026 import Guts
from ability.ability_027 import Static
from ability.ability_028 import Hydration
from ability.ability_029 import StickyHold
from ability.ability_030 import StormDrain
from ability.ability_031 import Stench
from ability.ability_032 import Aftermath
from ability.ability_033 import Chlorophyll
from ability.ability_034 import SwiftSwim
from ability.ability_035 import RainDish
from ability.ability_036 import EarlyBird
from ability.ability_037 import InnerFocus
from ability.ability_038 import IceBody
from ability.ability_039 import CuteCharm
from ability.ability_040 import Klutz
from ability.ability_041 import SnowCloak
from ability.ability_042 import Technician
from ability.ability_043 import Pickup
from ability.ability_044 import Insomnia
from ability.ability_045 import OwnTempo
from ability.ability_046 import Levitate
from ability.ability_047 import Scrappy
from ability.ability_048 import AngerPoint
from ability.ability_049 import Synchronize
from ability.ability_050 import NaturalCure
from ability.ability_051 import DrySkin
from ability.ability_052 import SnowWarning
from ability.ability_053 import PoisonPoint
from ability.ability_054 import Rivalry
from ability.ability_055 import SuctionCups
from ability.ability_056 import BattleArmor
from ability.ability_057 import Unburden
from ability.ability_058 import CloudNine
from ability.ability_059 import RunAway
from ability.ability_060 import FlashFire
from ability.ability_061 import HyperCutter
from ability.ability_062 import MoldBreaker
from ability.ability_063 import Swarm
from ability.ability_064 import WaterVeil
from ability.ability_065 import Heatproof
from ability.ability_066 import Sniper
from ability.ability_067 import NoGuard
from ability.ability_068 import Gluttony
from ability.ability_069 import ClearBody
from ability.ability_070 import LiquidOoze
from ability.ability_071 import Trace
from ability.ability_072 import Download
from ability.ability_073 import SpeedBoost
from ability.ability_074 import TintedLens
from ability.ability_075 import Steadfast
from ability.ability_076 import LeafGuard
from ability.ability_077 import SandStream
from ability.ability_078 import MagnetPull
from ability.ability_079 import ShellArmor
from ability.ability_080 import SolidRock
from ability.ability_081 import Adaptability
from ability.ability_082 import Immunity
from ability.ability_083 import SereneGrace
from ability.ability_084 import MarvelScale
from ability.ability_085 import MotorDrive
from ability.ability_086 import FlameBody
from ability.ability_087 import Hustle
from ability.ability_088 import Truant

# 特性のID（data/ability.jsonのキー） → 特性クラス
_ABILITY_CLASSES = {
    0: Overgrow,
    1: Blaze,
    2: Torrent,
    3: SandVeil,
    4: ArenaTrap,
    5: RockHead,
    6: LightningRod,
    7: PurePower,
    8: Damp,
    9: WaterAbsorb,
    10: Intimidate,
    11: QuickFeet,
    12: Oblivious,
    13: Forewarn,
    14: Soundproof,
    15: Filter,
    16: VoltAbsorb,
    17: Illuminate,
    18: EffectSpore,
    19: PoisonHeal,
    20: Sturdy,
    21: KeenEye,
    22: Pressure,
    23: SuperLuck,
    24: Anticipation,
    25: ThickFat,
    26: Guts,
    27: Static,
    28: Hydration,
    29: StickyHold,
    30: StormDrain,
    31: Stench,
    32: Aftermath,
    33: Chlorophyll,
    34: SwiftSwim,
    35: RainDish,
    36: EarlyBird,
    37: InnerFocus,
    38: IceBody,
    39: CuteCharm,
    40: Klutz,
    41: SnowCloak,
    42: Technician,
    43: Pickup,
    44: Insomnia,
    45: OwnTempo,
    46: Levitate,
    47: Scrappy,
    48: AngerPoint,
    49: Synchronize,
    50: NaturalCure,
    51: DrySkin,
    52: SnowWarning,
    53: PoisonPoint,
    54: Rivalry,
    55: SuctionCups,
    56: BattleArmor,
    57: Unburden,
    58: CloudNine,
    59: RunAway,
    60: FlashFire,
    61: HyperCutter,
    62: MoldBreaker,
    63: Swarm,
    64: WaterVeil,
    65: Heatproof,
    66: Sniper,
    67: NoGuard,
    68: Gluttony,
    69: ClearBody,
    70: LiquidOoze,
    71: Trace,
    72: Download,
    73: SpeedBoost,
    74: TintedLens,
    75: Steadfast,
    76: LeafGuard,
    77: SandStream,
    78: MagnetPull,
    79: ShellArmor,
    80: SolidRock,
    81: Adaptability,
    82: Immunity,
    83: SereneGrace,
    84: MarvelScale,
    85: MotorDrive,
    86: FlameBody,
    87: Hustle,
    88: Truant,
}


# 特性IDから特性クラスのインスタンスを生成する。特性ごとに状態（もらいびの発動済み等）を持つため、
# ポケモンごとに別々のインスタンスを作る
def create_ability(ability_id: int) -> BaseAbility:
    ability_class = _ABILITY_CLASSES.get(ability_id)
    if ability_class is None:
        return BaseAbility(ability_id)
    return ability_class()

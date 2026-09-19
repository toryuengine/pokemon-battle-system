from move.base_move import BaseMove
from move.leaf_storm import LeafStorm
from move.sludge_bomb import SludgeBomb
from move.amnesia import Amnesia
from move.sleep_powder import SleepPowder
from move.giga_drain import GigaDrain
from move.ingrain import Ingrain
from move.leech_seed import LeechSeed
from move.seed_bomb import SeedBomb
from move.earthquake import Earthquake
from move.outrage import Outrage
from move.curse import Curse
from move.frenzy_plant import FrenzyPlant
from move.hyper_beam import HyperBeam
from move.synthesis import Synthesis
from move.move_014 import かえんほうしゃ
from move.move_015 import エアスラッシュ
from move.move_016 import えんまく
from move.move_017 import こわいかお
from move.move_018 import オーバーヒート
from move.move_019 import ソーラービーム
from move.move_020 import おにび
from move.move_021 import にほんばれ
from move.flare_drive import FlareDrive
from move.crunch import Crunch
from move.dragon_claw import DragonClaw
from move.move_025 import ブラストバーン
from move.move_026 import きあいだま
from move.move_027 import げんしのちから
from move.move_028 import ハイドロポンプ
from move.move_029 import シグナルビーム
from move.move_030 import こごえるかぜ
from move.move_031 import ミラーコート
from move.move_032 import たきのぼり
from move.move_033 import きあいパンチ
from move.move_034 import かげぶんしん
from move.move_035 import アクアリング
from move.move_036 import アクアテール
from move.move_037 import ゆきなだれ
from move.move_038 import しねんのずつき
from move.move_039 import ハイドロカノン
from move.move_040 import れいとうビーム
from move.move_041 import どくどく
from move.move_042 import みがわり
from move.move_043 import しぼりとる
from move.move_044 import ひかりのかべ
from move.move_045 import リフレクター
from move.move_046 import ほのおのパンチ
from move.move_047 import かみなりパンチ
from move.move_048 import シャドークロー
from move.move_049 import でんこうせっか
from move.move_050 import きしかいせい
from move.move_051 import こらえる
from move.move_052 import つばめがえし
from move.move_053 import こおりのキバ
from move.move_054 import いわなだれ
from move.move_055 import ばかぢから
from move.move_056 import りゅうのまい
from move.move_057 import リーフブレード
from move.move_058 import いやなおと
from move.move_059 import シザークロス
from move.move_060 import つじぎり
from move.move_061 import りゅうのはどう
from move.move_062 import ブレイズキック
from move.move_063 import ストーンエッジ
from move.move_064 import れいとうパンチ
from move.move_065 import まもる
from move.move_066 import アームハンマー
from move.move_067 import だくりゅう
from move.move_068 import だいちのちから
from move.move_069 import カウンター
from move.move_070 import くさむすび
from move.move_071 import ウッドハンマー
from move.move_072 import インファイト
from move.move_073 import とんぼがえり
from move.move_074 import ねこだまし
from move.move_075 import ダストシュート
from move.move_076 import メタルクロー
from move.move_077 import かわらわり
from move.move_078 import はたきおとす
from move.move_079 import ドリルくちばし
from move.move_080 import アクアジェット
from move.move_081 import なみのり
from move.move_082 import ふぶき
from move.move_083 import ラスターカノン
from move.move_084 import おどろかす
from move.move_085 import すなじごく
from move.move_086 import トライアタック
from move.move_087 import すなあらし
from move.move_088 import じわれ
from move.move_089 import ギガインパクト
from move.move_090 import きりさく
from move.move_091 import ボーンラッシュ
from move.move_092 import アイアンテール
from move.move_093 import アイアンヘッド
from move.move_094 import ドレインパンチ
from move.move_095 import どくづき
from move.move_096 import みきり
from move.move_097 import じこさいせい
from move.move_098 import サイコキネシス
from move.move_099 import シャドーボール
from move.move_100 import めいそう
from move.move_101 import サイコカッター
from move.move_102 import ダイビング
from move.move_103 import あくび
from move.move_104 import おんがえし
from move.move_105 import でんじは
from move.move_106 import からげんき
from move.move_107 import ほのおのキバ
from move.move_108 import かみなりのキバ
from move.move_109 import しっぺがえし
from move.move_110 import あくまのキッス
from move.move_111 import うそなき
from move.move_112 import ゆめくい
from move.move_113 import ほろびのうた
from move.move_114 import くろいまなざし
from move.move_115 import エナジーボール
from move.move_116 import まねっこ
from move.move_117 import ものまね
from move.move_118 import さいみんじゅつ
from move.move_119 import _10まんボルト
from move.move_120 import チャージビーム
from move.move_121 import ほうでん
from move.move_122 import あやしいひかり
from move.move_123 import メロメロ
from move.move_124 import かみなり
from move.move_125 import あまごい
from move.move_126 import スカイアッパー
from move.move_127 import ばくれつパンチ
from move.move_128 import キノコのほうし
from move.move_129 import ジャイロボール
from move.move_130 import むしくい
from move.move_131 import リベンジ
from move.move_132 import ステルスロック
from move.move_133 import どくびし
from move.move_134 import まきびし
from move.move_135 import あなをほる
from move.move_136 import いばる
from move.move_137 import だいばくはつ
from move.move_138 import すてみタックル
from move.move_139 import はがねのつばさ
from move.move_140 import ほえる
from move.move_141 import そらをとぶ
from move.move_142 import はねやすめ
from move.move_143 import ブレイブバード
from move.move_144 import ふいうち
from move.move_145 import ちょうはつ
from move.move_146 import おしおき
from move.move_147 import あばれる
from move.move_148 import つっぱり
from move.move_149 import なげつける
from move.move_150 import クロスチョップ
from move.move_151 import ぎんいろのかぜ
from move.move_152 import エアカッター
from move.move_153 import あやしいかぜ
from move.move_154 import かいふくしれい
from move.move_155 import みちづれ
from move.move_156 import おいうち
from move.move_157 import こうげきしれい
from move.move_158 import ぼうぎょしれい
from move.move_159 import たたきつける
from move.move_160 import てんしのキッス
from move.move_161 import わるだくみ
from move.move_162 import ボルテッカー
from move.move_163 import ずつき
from move.move_164 import アンコール
from move.move_165 import かなしばり
from move.move_166 import ぜったいれいど
from move.move_167 import つのドリル
from move.move_168 import ねむる
from move.move_169 import ねごと
from move.move_170 import かみつく
from move.move_171 import スピードスター
from move.move_172 import がむしゃら
from move.move_173 import どろばくだん
from move.move_174 import あくのはどう
from move.move_175 import やつあたり
from move.move_176 import つるぎのまい
from move.move_177 import いえき
from move.move_178 import はきだす
from move.move_179 import のみこむ
from move.move_180 import たくわえる
from move.move_181 import フラッシュ
from move.move_182 import でんじふゆう
from move.move_183 import はっぱカッター
from move.move_184 import だましうち
from move.move_185 import ハイパーボイス
from move.move_186 import じんつうりき
from move.move_187 import みずのはどう
from move.move_188 import いちゃもん
from move.move_189 import こおりのつぶて
from move.move_190 import あられ
from move.move_191 import あまえる
from move.move_192 import ピヨピヨパンチ
from move.move_193 import じこあんじ
from move.move_194 import ダブルアタック
from move.move_195 import とっておき
from move.move_196 import トリックルーム
from move.move_197 import あくむ
from move.move_198 import メガホーン
from move.move_199 import でんげきは
from move.move_200 import おんねん
from move.move_201 import みらいよち
from move.move_202 import しおみず
from move.move_203 import ミルクのみ
from move.move_204 import うたう
from move.move_205 import ドラゴンダイブ
from move.move_206 import ゴッドバード
from move.move_207 import りゅうせいぐん
from move.move_208 import くさぶえ
from move.move_209 import どくどくのキバ
from move.move_210 import にどげり
from move.move_211 import てっぺき
from move.move_212 import ブレイククロー
from move.move_213 import クロスポイズン
from move.move_214 import メタルバースト
from move.move_215 import パワージェム
from move.move_216 import マジカルリーフ
from move.move_217 import おきみやげ
from move.move_218 import バトンタッチ
from move.move_219 import トリック
from move.move_220 import しんくうは
from move.move_221 import ビルドアップ
from move.move_222 import だいもんじ
from move.move_223 import かげうち
from move.move_224 import ちいさくなる
from move.move_225 import とける
from move.move_226 import うらみ
from move.move_227 import はらだいこ
from move.move_228 import じたばた
from move.move_229 import ハサミギロチン
from move.move_230 import バレットパンチ
from move.move_231 import うずしお
from move.move_232 import もろはのずつき
from move.move_233 import つぼをつく
from move.move_234 import とおぼえ
from move.move_235 import じゅうでん
from move.move_236 import ねっぷう
from move.move_237 import みやぶる
from move.move_238 import パワートリック
from move.move_239 import まきつく
from move.move_240 import しびれごな
from move.move_241 import どろかけ
from move.move_242 import ウェザーボール
from move.move_243 import ついばむ
from move.move_244 import バリアー
from move.move_245 import リサイクル
from move.move_246 import のしかかり
from move.move_247 import パワーウィップ
from move.move_248 import むしのさざめき
from move.move_249 import こうそくいどう
from move.move_250 import すなかけ
from move.move_251 import あさのひざし
from move.move_252 import きりふだ
from move.move_253 import つきのひかり
from move.move_254 import はどうだん
from move.move_255 import なまける
from move.move_256 import マグネットボム
from move.move_257 import シャドーパンチ
from move.move_258 import いたみわけ
from move.move_259 import つつく
from move.move_260 import たつまき
from move.move_261 import ミラーショット
from move.move_262 import がんせきほう
from move.move_263 import テクスチャー2
from move.move_264 import タマゴうみ
from move.move_265 import しんそく
from move.move_266 import コメットパンチ

_MOVE_CLASSES = {
    0: LeafStorm,
    1: SludgeBomb,
    2: Amnesia,
    3: SleepPowder,
    4: GigaDrain,
    5: Ingrain,
    6: LeechSeed,
    7: SeedBomb,
    8: Earthquake,
    9: Outrage,
    10: Curse,
    11: FrenzyPlant,
    12: HyperBeam,
    13: Synthesis,
    14: かえんほうしゃ,
    15: エアスラッシュ,
    16: えんまく,
    17: こわいかお,
    18: オーバーヒート,
    19: ソーラービーム,
    20: おにび,
    21: にほんばれ,
    22: FlareDrive,
    23: Crunch,
    24: DragonClaw,
    25: ブラストバーン,
    26: きあいだま,
    27: げんしのちから,
    28: ハイドロポンプ,
    29: シグナルビーム,
    30: こごえるかぜ,
    31: ミラーコート,
    32: たきのぼり,
    33: きあいパンチ,
    34: かげぶんしん,
    35: アクアリング,
    36: アクアテール,
    37: ゆきなだれ,
    38: しねんのずつき,
    39: ハイドロカノン,
    40: れいとうビーム,
    41: どくどく,
    42: みがわり,
    43: しぼりとる,
    44: ひかりのかべ,
    45: リフレクター,
    46: ほのおのパンチ,
    47: かみなりパンチ,
    48: シャドークロー,
    49: でんこうせっか,
    50: きしかいせい,
    51: こらえる,
    52: つばめがえし,
    53: こおりのキバ,
    54: いわなだれ,
    55: ばかぢから,
    56: りゅうのまい,
    57: リーフブレード,
    58: いやなおと,
    59: シザークロス,
    60: つじぎり,
    61: りゅうのはどう,
    62: ブレイズキック,
    63: ストーンエッジ,
    64: れいとうパンチ,
    65: まもる,
    66: アームハンマー,
    67: だくりゅう,
    68: だいちのちから,
    69: カウンター,
    70: くさむすび,
    71: ウッドハンマー,
    72: インファイト,
    73: とんぼがえり,
    74: ねこだまし,
    75: ダストシュート,
    76: メタルクロー,
    77: かわらわり,
    78: はたきおとす,
    79: ドリルくちばし,
    80: アクアジェット,
    81: なみのり,
    82: ふぶき,
    83: ラスターカノン,
    84: おどろかす,
    85: すなじごく,
    86: トライアタック,
    87: すなあらし,
    88: じわれ,
    89: ギガインパクト,
    90: きりさく,
    91: ボーンラッシュ,
    92: アイアンテール,
    93: アイアンヘッド,
    94: ドレインパンチ,
    95: どくづき,
    96: みきり,
    97: じこさいせい,
    98: サイコキネシス,
    99: シャドーボール,
    100: めいそう,
    101: サイコカッター,
    102: ダイビング,
    103: あくび,
    104: おんがえし,
    105: でんじは,
    106: からげんき,
    107: ほのおのキバ,
    108: かみなりのキバ,
    109: しっぺがえし,
    110: あくまのキッス,
    111: うそなき,
    112: ゆめくい,
    113: ほろびのうた,
    114: くろいまなざし,
    115: エナジーボール,
    116: まねっこ,
    117: ものまね,
    118: さいみんじゅつ,
    119: _10まんボルト,
    120: チャージビーム,
    121: ほうでん,
    122: あやしいひかり,
    123: メロメロ,
    124: かみなり,
    125: あまごい,
    126: スカイアッパー,
    127: ばくれつパンチ,
    128: キノコのほうし,
    129: ジャイロボール,
    130: むしくい,
    131: リベンジ,
    132: ステルスロック,
    133: どくびし,
    134: まきびし,
    135: あなをほる,
    136: いばる,
    137: だいばくはつ,
    138: すてみタックル,
    139: はがねのつばさ,
    140: ほえる,
    141: そらをとぶ,
    142: はねやすめ,
    143: ブレイブバード,
    144: ふいうち,
    145: ちょうはつ,
    146: おしおき,
    147: あばれる,
    148: つっぱり,
    149: なげつける,
    150: クロスチョップ,
    151: ぎんいろのかぜ,
    152: エアカッター,
    153: あやしいかぜ,
    154: かいふくしれい,
    155: みちづれ,
    156: おいうち,
    157: こうげきしれい,
    158: ぼうぎょしれい,
    159: たたきつける,
    160: てんしのキッス,
    161: わるだくみ,
    162: ボルテッカー,
    163: ずつき,
    164: アンコール,
    165: かなしばり,
    166: ぜったいれいど,
    167: つのドリル,
    168: ねむる,
    169: ねごと,
    170: かみつく,
    171: スピードスター,
    172: がむしゃら,
    173: どろばくだん,
    174: あくのはどう,
    175: やつあたり,
    176: つるぎのまい,
    177: いえき,
    178: はきだす,
    179: のみこむ,
    180: たくわえる,
    181: フラッシュ,
    182: でんじふゆう,
    183: はっぱカッター,
    184: だましうち,
    185: ハイパーボイス,
    186: じんつうりき,
    187: みずのはどう,
    188: いちゃもん,
    189: こおりのつぶて,
    190: あられ,
    191: あまえる,
    192: ピヨピヨパンチ,
    193: じこあんじ,
    194: ダブルアタック,
    195: とっておき,
    196: トリックルーム,
    197: あくむ,
    198: メガホーン,
    199: でんげきは,
    200: おんねん,
    201: みらいよち,
    202: しおみず,
    203: ミルクのみ,
    204: うたう,
    205: ドラゴンダイブ,
    206: ゴッドバード,
    207: りゅうせいぐん,
    208: くさぶえ,
    209: どくどくのキバ,
    210: にどげり,
    211: てっぺき,
    212: ブレイククロー,
    213: クロスポイズン,
    214: メタルバースト,
    215: パワージェム,
    216: マジカルリーフ,
    217: おきみやげ,
    218: バトンタッチ,
    219: トリック,
    220: しんくうは,
    221: ビルドアップ,
    222: だいもんじ,
    223: かげうち,
    224: ちいさくなる,
    225: とける,
    226: うらみ,
    227: はらだいこ,
    228: じたばた,
    229: ハサミギロチン,
    230: バレットパンチ,
    231: うずしお,
    232: もろはのずつき,
    233: つぼをつく,
    234: とおぼえ,
    235: じゅうでん,
    236: ねっぷう,
    237: みやぶる,
    238: パワートリック,
    239: まきつく,
    240: しびれごな,
    241: どろかけ,
    242: ウェザーボール,
    243: ついばむ,
    244: バリアー,
    245: リサイクル,
    246: のしかかり,
    247: パワーウィップ,
    248: むしのさざめき,
    249: こうそくいどう,
    250: すなかけ,
    251: あさのひざし,
    252: きりふだ,
    253: つきのひかり,
    254: はどうだん,
    255: なまける,
    256: マグネットボム,
    257: シャドーパンチ,
    258: いたみわけ,
    259: つつく,
    260: たつまき,
    261: ミラーショット,
    262: がんせきほう,
    263: テクスチャー2,
    264: タマゴうみ,
    265: しんそく,
    266: コメットパンチ,
}


def create_move(move_id: int) -> BaseMove:
    move_class = _MOVE_CLASSES.get(move_id)
    if move_class is None:
        return BaseMove(move_id)
    return move_class()

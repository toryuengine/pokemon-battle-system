from move.base_move import BaseMove

WEATHER_BALL_BASE_TYPE = "ノーマル"
WEATHER_BALL_TYPES = {
    "sun": "ほのお",
    "rain": "みず",
    "sandstorm": "いわ",
    "hail": "こおり",
}


# ウェザーボール: 天候があるとき、天候に対応するタイプ（晴れ→ほのお・雨→みず・すなあらし→いわ・あられ→こおり）になり、
# 威力が2倍（100）になる。晴れ・雨のほのお/みず技の威力補正も重ねて掛かる。ノーてんき等で天候が無効なら変化しない
class WeatherBall(BaseMove):
    def __init__(self):
        super().__init__(id=242)
        self.effects = []

    # タイプはタイプ一致・相性・特性（ちくでん等）・半減実の判定でも使うため、技を出す直前に決めておく
    def prepare_for_use(self, battle, attacker, defender):
        self.type = WEATHER_BALL_TYPES.get(battle.get_effective_weather(), WEATHER_BALL_BASE_TYPE)

    def get_power(self, battle, attacker, defender) -> int:
        if self.type != WEATHER_BALL_BASE_TYPE:
            return self.power * 2
        return self.power

from ability.shared import WeatherHealAbility


# アイスボディ: あられの間、ターン終了時に最大HPの1/16回復する。あられのダメージを受けない
class IceBody(WeatherHealAbility):
    weather = "hail"
    weather_immunities = frozenset({"hail"})

    def __init__(self):
        super().__init__(id=38)

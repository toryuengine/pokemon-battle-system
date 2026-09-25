from ability.shared import WeatherEvasionAbility


# ゆきがくれ: あられの間、受ける技の命中率が0.8倍。あられのダメージを受けない
class SnowCloak(WeatherEvasionAbility):
    weather = "hail"
    weather_immunities = frozenset({"hail"})

    def __init__(self):
        super().__init__(id=41)

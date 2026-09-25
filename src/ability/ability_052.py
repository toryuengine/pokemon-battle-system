from ability.shared import WeatherSetterAbility


# ゆきふらし: 場に出た時、天候をあられにする
class SnowWarning(WeatherSetterAbility):
    weather = "hail"

    def __init__(self):
        super().__init__(id=52)

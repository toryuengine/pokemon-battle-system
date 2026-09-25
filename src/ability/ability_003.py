from ability.shared import WeatherEvasionAbility


# すながくれ: すなあらしの間、受ける技の命中率が0.8倍。すなあらしのダメージを受けない
class SandVeil(WeatherEvasionAbility):
    weather = "sandstorm"
    weather_immunities = frozenset({"sandstorm"})

    def __init__(self):
        super().__init__(id=3)

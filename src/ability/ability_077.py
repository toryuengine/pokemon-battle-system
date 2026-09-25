from ability.shared import WeatherSetterAbility


# すなおこし: 場に出た時、天候をすなあらしにする
class SandStream(WeatherSetterAbility):
    weather = "sandstorm"

    def __init__(self):
        super().__init__(id=77)

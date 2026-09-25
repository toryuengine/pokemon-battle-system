from ability.shared import WeatherSpeedAbility


# すいすい: あめの間、素早さが2倍
class SwiftSwim(WeatherSpeedAbility):
    weather = "rain"

    def __init__(self):
        super().__init__(id=34)

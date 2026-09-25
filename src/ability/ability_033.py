from ability.shared import WeatherSpeedAbility


# ようりょくそ: にほんばれの間、素早さが2倍
class Chlorophyll(WeatherSpeedAbility):
    weather = "sun"

    def __init__(self):
        super().__init__(id=33)

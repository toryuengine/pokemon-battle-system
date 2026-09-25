from ability.shared import WeatherHealAbility


# あめうけざら: あめの間、ターン終了時に最大HPの1/16回復する
class RainDish(WeatherHealAbility):
    weather = "rain"

    def __init__(self):
        super().__init__(id=35)

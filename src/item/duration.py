from item.base_item import BaseItem

EXTENDED_WEATHER_DURATION = 8
EXTENDED_SCREEN_DURATION = 8


# あついいわ・しめったいわ・つめたいいわ: 持ち主が起こしたweatherの天候が8ターン続く
class WeatherRock(BaseItem):
    def __init__(self, id: int, weather: str):
        super().__init__(id)
        self.weather = weather

    def get_weather_duration(self, weather: str, duration: int) -> int:
        return EXTENDED_WEATHER_DURATION if weather == self.weather else duration


# ひかりのねんど: 持ち主が張ったリフレクター・ひかりのかべが8ターン続く
class LightClay(BaseItem):
    def get_screen_duration(self, duration: int) -> int:
        return EXTENDED_SCREEN_DURATION


# ねばりのかぎづめ: しめつけ系の技が5ターン続く（しめつけ系の技が未実装のため今は効果なし）
class GripClaw(BaseItem):
    pass

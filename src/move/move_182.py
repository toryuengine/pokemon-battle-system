from move.base_move import BaseMove


# でんじふゆう: 5ターンの間、じめん技・まきびし・どくびしを受けなくなる
class MagnetRise(BaseMove):
    def __init__(self):
        super().__init__(id=182)
        self.effects = [("magnet_rise",)]

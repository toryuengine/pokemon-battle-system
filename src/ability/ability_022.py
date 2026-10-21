from ability.shared import AnnouncedOnSwitchInAbility


# プレッシャー: 自分に向けられた相手の技のPPを1多く減らす。場に出た時にメッセージが出る
class Pressure(AnnouncedOnSwitchInAbility):
    increases_opponent_pp_usage = True

    def __init__(self):
        super().__init__(id=22)

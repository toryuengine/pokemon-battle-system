from ability.base_ability import BaseAbility


# プレッシャー: 自分に向けられた相手の技のPPを1多く減らす
class Pressure(BaseAbility):
    increases_opponent_pp_usage = True

    def __init__(self):
        super().__init__(id=22)

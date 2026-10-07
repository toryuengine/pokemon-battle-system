from move.base_move import BaseMove


# ちょうはつ: 相手を3〜5ターンの間、変化技を使えない状態にする
class Taunt(BaseMove):
    def __init__(self):
        super().__init__(id=145)
        self.effects = [("taunt",)]

from move.base_move import BaseMove


# ねごと: ねむっている間だけ使え、自分の他の技からランダムに1つ選んで使う（呼び出した技のPPは減らない）
class SleepTalk(BaseMove):
    def __init__(self):
        super().__init__(id=169)
        self.effects = []
        self.usable_while_asleep = True
        self.calls_own_random_move = True
        self.cannot_be_called_by_sleep_talk = True

from move.base_move import BaseMove


# あばれる: 2〜3ターンの間この技しか出せなくなり（PPは最初のターンだけ消費する）、最後のターンを終えると疲れてこんらんする
# 途中で行動できなかった・交代した場合は、こんらんせずに固定が解ける
class Thrash(BaseMove):
    def __init__(self):
        super().__init__(id=147)
        self.effects = []
        self.is_rampage = True

from move.base_move import BaseMove


# こらえる: 第4世代の優先度は+3（まもる・みきりと同じ。+4になったのは第5世代以降）
class Endure(BaseMove):
    def __init__(self):
        super().__init__(id=51)
        self.effects = [("endure",)]
        self.priority = 3

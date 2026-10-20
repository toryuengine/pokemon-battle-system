from move.base_move import BaseMove


# しんぴのまもり: 5ターンの間、自分の場のポケモンが相手から状態異常・こんらんにされなくなる
class Safeguard(BaseMove):
    def __init__(self):
        super().__init__(id=272)
        self.effects = [("safeguard",)]

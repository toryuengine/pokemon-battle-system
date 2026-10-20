from move.base_move import BaseMove


# とびはねる: 1ターン目に空高く跳び（そらをとぶと同じく、かみなり・たつまき・スカイアッパー以外の技を受けない）、
# 2ターン目に攻撃する。30%の確率で相手をまひ状態にする
class Bounce(BaseMove):
    def __init__(self):
        super().__init__(id=273)
        self.makes_contact = True
        self.effects = [("status", "target", "paralysis", 0.3)]
        self.requires_charge_turn = True
        self.charge_is_invulnerable = True

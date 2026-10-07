from move.base_move import BaseMove


# どくどくのキバ: 30%の確率で相手をもうどく状態にする
class PoisonFang(BaseMove):
    def __init__(self):
        super().__init__(id=209)
        self.makes_contact = True
        self.effects = [('status', 'target', 'toxic', 0.3)]

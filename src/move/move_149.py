from move.base_move import BaseMove


# なげつける: 持っている持ち物を投げつける。威力は持ち物によって決まり、きのみ・しろいハーブは相手が使った扱い、
# どくどくだまはどく、おうじゃのしるし・するどいキバはひるみの効果を相手に与える。持ち物が無ければ失敗する
# 投げた持ち物は消費した扱いになる（リサイクルで取り戻せる）
class Fling(BaseMove):
    def __init__(self):
        super().__init__(id=149)
        self.effects = [("fling",)]
        # 今回投げつけた持ち物（威力と追加効果の判定に使う）
        self.flung_item = None

    # 技を出した時点で持ち物を手放す（持ち物が無ければ失敗する）
    def try_execute(self, battle, attacker, defender) -> bool:
        self.flung_item = attacker.item
        if self.flung_item is None:
            return False
        battle.consume_item(attacker)
        return True

    def get_power(self, battle, attacker, defender) -> int:
        return self.flung_item.fling_power if self.flung_item is not None else self.power

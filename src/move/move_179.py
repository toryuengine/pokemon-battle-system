from move.base_move import BaseMove


# のみこむ: たくわえた回数に応じて回復する（1回: 1/4、2回: 1/2、3回: 全回復）。たくわえていなければ失敗する
class Swallow(BaseMove):
    def __init__(self):
        super().__init__(id=179)
        self.effects = [("swallow",)]

    # たくわえていなければ失敗する
    def try_execute(self, battle, attacker, defender) -> bool:
        return attacker.current_status.stockpile_count > 0

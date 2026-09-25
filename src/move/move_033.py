from move.base_move import BaseMove


# きあいパンチ: 優先度-3。このターン、技を出す前に攻撃を受けてダメージを負っていると集中が途切れて失敗する
# (みがわりが受けた攻撃ではダメージを負っていない扱い。PPは消費する)
class FocusPunch(BaseMove):
    def __init__(self):
        super().__init__(id=33)
        self.effects = []
        self.priority = -3
        # 集中している間に攻撃を受けると失敗する技なので、ねごとでは呼び出せない
        self.cannot_be_called_by_sleep_talk = True

    def try_execute(self, battle, attacker, defender) -> bool:
        return attacker.current_status.damaged_by_this_turn is None

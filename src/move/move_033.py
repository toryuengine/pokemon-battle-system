from move.base_move import BaseMove


# きあいパンチ
class FocusPunch(BaseMove):
    def __init__(self):
        super().__init__(id=33)
        self.effects = []
        self.priority = -3
        # 集中している間に攻撃を受けると失敗する技なので、ねごとでは呼び出せない
        self.cannot_be_called_by_sleep_talk = True

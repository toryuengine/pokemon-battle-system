from move.base_move import BaseMove


# パワートリック
class PowerTrick(BaseMove):
    def __init__(self):
        super().__init__(id=238)  # 変身・コピー系の特殊な仕様は未実装
        self.effects = []

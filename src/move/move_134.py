from move.base_move import BaseMove


# まきびし
class Spikes(BaseMove):
    def __init__(self):
        super().__init__(id=134)  # 設置技（場に効果を残すタイプ）は未実装
        self.effects = []

from move.base_move import BaseMove


# つのドリル
class HornDrill(BaseMove):
    def __init__(self):
        super().__init__(id=167)  # 一撃必殺技は未実装
        self.effects = []

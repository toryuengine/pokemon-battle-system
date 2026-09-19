from move.base_move import BaseMove


# リフレクター
class Reflect(BaseMove):
    def __init__(self):
        super().__init__(id=45)  # 壁によるダメージ軽減は未実装
        self.effects = []

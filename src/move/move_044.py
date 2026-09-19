from move.base_move import BaseMove


# ひかりのかべ
class LightScreen(BaseMove):
    def __init__(self):
        super().__init__(id=44)  # 壁によるダメージ軽減は未実装
        self.effects = []

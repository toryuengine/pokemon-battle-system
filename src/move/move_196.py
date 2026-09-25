from move.base_move import BaseMove


# トリックルーム
class TrickRoom(BaseMove):
    def __init__(self):
        super().__init__(id=196)
        self.effects = [("trick_room",)]
        # 後攻技（優先度-7）
        self.priority = -7

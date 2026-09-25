from move.base_move import BaseMove


# とっておき: 場に出てから、技構成の他の技を全て1回以上使っていないと失敗する。
# 技構成がとっておきだけの場合も失敗する
class LastResort(BaseMove):
    def __init__(self):
        super().__init__(id=195)
        self.effects = []

    def try_execute(self, battle, attacker, defender) -> bool:
        other_moves = [move for move in attacker.moves if move.id != self.id]
        if not other_moves:
            return False
        used_move_ids = attacker.current_status.used_move_ids
        return all(move.id in used_move_ids for move in other_moves)

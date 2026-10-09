from move.base_move import CATEGORY_STATUS, BaseMove


# ふいうち: 優先度+1。相手がこのターン攻撃技を選んでいない（変化技・交代）、または相手が既に行動していれば失敗する
class SuckerPunch(BaseMove):
    def __init__(self):
        super().__init__(id=144)
        self.makes_contact = True
        self.effects = []
        self.priority = 1

    def try_execute(self, battle, attacker, defender) -> bool:
        selected_move = defender.current_status.selected_move_this_turn
        if defender.current_status.has_moved_this_turn or selected_move is None:
            return False
        return selected_move.category != CATEGORY_STATUS

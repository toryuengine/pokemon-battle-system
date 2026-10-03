from move.base_move import BaseMove


# ねこだまし: 優先度+1。場に出てから最初のターンにしか成功しない。成功すれば必ずひるませる
class FakeOut(BaseMove):
    def __init__(self):
        super().__init__(id=74)
        self.makes_contact = True
        self.effects = [('flinch', 'target', 1.0)]
        self.priority = 1

    def try_execute(self, battle, attacker, defender) -> bool:
        return attacker.current_status.turns_on_field == 1

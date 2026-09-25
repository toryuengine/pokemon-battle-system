from ability.base_ability import BaseAbility


# なまけ: 1回行動すると、次のターンは行動できない（なまける）
class Truant(BaseAbility):
    def __init__(self):
        super().__init__(id=88)
        # 次に行動しようとしたターンになまけるかどうか。場に出た最初のターンは行動できる
        self.is_loafing = False

    def on_switch_in(self, battle, pokemon):
        self.is_loafing = False

    def on_before_action(self, battle, pokemon) -> bool:
        if self.is_loafing:
            self.is_loafing = False
            return False
        self.is_loafing = True
        return True

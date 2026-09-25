from move.base_move import BaseMove


# おいうち: 相手が手動で交代しようとしていれば、交代する前に威力2倍で攻撃する
# (瀕死・とんぼがえり・バトンタッチ・ほえるによる交代に対しては、第4世代でも発動しない)
class Pursuit(BaseMove):
    def __init__(self):
        super().__init__(id=156)
        self.effects = []
        self.hits_switching_target = True

    def get_power(self, battle, attacker, defender) -> int:
        if defender.current_status.is_switching_out:
            return self.power * 2
        return self.power

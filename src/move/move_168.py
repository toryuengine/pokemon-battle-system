from move.base_move import BaseMove


# ねむる: HPを全回復し、状態異常を治してから2ターンねむる
# HPが満タン・既にねむっている・ねむり状態にならない（ふみん、にほんばれ中のリーフガード）なら失敗する
class Rest(BaseMove):
    def __init__(self):
        super().__init__(id=168)
        self.effects = [('rest',)]

    def try_execute(self, battle, attacker, defender) -> bool:
        status = attacker.current_status
        if status.current_hp >= attacker.status.hp or status.status_condition == "sleep":
            return False
        return battle.can_receive_status(attacker, "sleep")

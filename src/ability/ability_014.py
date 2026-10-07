from ability.base_ability import BaseAbility

# 音の技のID（くさぶえ・ハイパーボイス・ほろびのうた・ほえる・いやなおと・うたう・むしのさざめき）
SOUND_MOVE_IDS = {58, 113, 140, 185, 204, 208, 248}


# ぼうおん: 音の技を受けない
class Soundproof(BaseAbility):
    is_breakable = True

    def __init__(self):
        super().__init__(id=14)

    def on_try_hit(self, battle, attacker, defender, move) -> bool:
        return move.id in SOUND_MOVE_IDS

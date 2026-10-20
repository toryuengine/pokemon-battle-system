from ability.base_ability import BaseAbility


# マジックガード: 技による攻撃以外ではダメージを受けない（Battle.apply_indirect_damageで判定する）
# 防ぐもの: どく・やけど・のろい・あくむ・しめつけ・やどりぎのタネ・天候・まきびし・ステルスロック・反動（わるあがきを除く）・
# いのちのたま・くろいヘドロ・ゆうばく・ヘドロえき
# 防がないもの: こんらんの自傷（攻撃扱い）・わるあがきの反動・自分で払うHP（はらだいこ・みがわり・のろい）・いたみわけ
# 第4世代だけの仕様として、まひで動けなくなることが無く（素早さは下がる）、どくびしでどくにならない
class MagicGuard(BaseAbility):
    prevents_indirect_damage = True

    def __init__(self):
        super().__init__(id=90)

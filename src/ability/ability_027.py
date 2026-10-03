from ability.shared import ContactStatusAbility


# せいでんき: 接触技を受けると30%の確率で相手をまひにする（第4世代なので、でんきタイプもまひになる）
class Static(ContactStatusAbility):
    conditions = ("paralysis",)

    def __init__(self):
        super().__init__(id=27)

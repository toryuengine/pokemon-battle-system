from readpokemondata import load_move_data


class BaseMove:
    def __init__(self, id: int):
        data = load_move_data()[str(id)]

        self.id = id
        self.name = data["name"]
        self.type = data["type"]
        self.category = data["category"]
        self.power = data["power"]
        self.pp = data["pp"]
        self.hitrate = data["hitrate"]

    # 追加効果が無い技はここで何もしない。追加効果がある技はサブクラスでオーバーライドする
    def apply_effect(self, battle, attacker, defender):
        pass

    def __repr__(self):
        parts = []
        for key, value in vars(self).items():
            parts.append(f"{key}={value!r}")
        return f"{self.__class__.__name__}({', '.join(parts)})"

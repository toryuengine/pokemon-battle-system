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

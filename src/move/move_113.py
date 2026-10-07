from move.base_move import BaseMove


# ほろびのうた
class PerishSong(BaseMove):
    def __init__(self):
        super().__init__(id=113)
        self.effects = [("perish_song",)]

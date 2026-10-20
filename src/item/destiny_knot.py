from item.base_item import BaseItem


# あかいいと: 持ち主がメロメロ状態になると、メロメロにした相手もメロメロ状態にする（消費しない）
# 相手がどんかん・既にメロメロ状態なら、相手はメロメロにならない（メロメロ（技）と同じ判定）
class DestinyKnot(BaseItem):
    def on_infatuated(self, battle, pokemon, source):
        battle.perform_attract(pokemon, source)
